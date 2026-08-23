#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/landlock.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef O_PATH
#define O_PATH 010000000
#endif

static int ll_create(const struct landlock_ruleset_attr *attr, size_t size, __u32 flags) {
    return (int)syscall(SYS_landlock_create_ruleset, attr, size, flags);
}

static int ll_add(int ruleset_fd, enum landlock_rule_type type,
                  const void *attr, __u32 flags) {
    return (int)syscall(SYS_landlock_add_rule, ruleset_fd, type, attr, flags);
}

static int ll_restrict(int ruleset_fd, __u32 flags) {
    return (int)syscall(SYS_landlock_restrict_self, ruleset_fd, flags);
}

static __u64 handled_rights(int abi) {
    __u64 rights = LANDLOCK_ACCESS_FS_EXECUTE |
                   LANDLOCK_ACCESS_FS_WRITE_FILE |
                   LANDLOCK_ACCESS_FS_READ_FILE |
                   LANDLOCK_ACCESS_FS_READ_DIR |
                   LANDLOCK_ACCESS_FS_REMOVE_DIR |
                   LANDLOCK_ACCESS_FS_REMOVE_FILE |
                   LANDLOCK_ACCESS_FS_MAKE_CHAR |
                   /* Deliberately do not handle MAKE_DIR. NVIDIA's userspace
                    * driver probes already-existing parent directories with
                    * mkdir(2) and relies on the native EEXIST result. Denying
                    * that probe early changes cudaGetDeviceCount() into
                    * CUDA_ERROR_OPERATING_SYSTEM. File creation/writes,
                    * removal, rename/refer, links, sockets and device nodes
                    * remain mediated; the residual permission is creation of
                    * empty directories where normal Unix DAC already allows it. */
                   LANDLOCK_ACCESS_FS_MAKE_REG |
                   LANDLOCK_ACCESS_FS_MAKE_SOCK |
                   LANDLOCK_ACCESS_FS_MAKE_FIFO |
                   LANDLOCK_ACCESS_FS_MAKE_BLOCK |
                   LANDLOCK_ACCESS_FS_MAKE_SYM;
    if (abi >= 2) rights |= LANDLOCK_ACCESS_FS_REFER;
    if (abi >= 3) rights |= LANDLOCK_ACCESS_FS_TRUNCATE;
    return rights;
}

static __u64 readonly_rights(void) {
    return LANDLOCK_ACCESS_FS_EXECUTE |
           LANDLOCK_ACCESS_FS_READ_FILE |
           LANDLOCK_ACCESS_FS_READ_DIR;
}

static __u64 device_rights(void) {
    return LANDLOCK_ACCESS_FS_EXECUTE |
           LANDLOCK_ACCESS_FS_WRITE_FILE |
           LANDLOCK_ACCESS_FS_READ_FILE |
           LANDLOCK_ACCESS_FS_READ_DIR;
}

static int add_path_rule(int ruleset_fd, const char *path, __u64 allowed) {
    int path_fd = open(path, O_PATH | O_CLOEXEC);
    if (path_fd < 0) {
        fprintf(stderr, "landlock: cannot open %s: %s\n", path, strerror(errno));
        return -1;
    }
    struct landlock_path_beneath_attr rule = {
        .allowed_access = allowed,
        .parent_fd = path_fd,
    };
    int rc = ll_add(ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &rule, 0);
    if (rc < 0) {
        fprintf(stderr, "landlock: cannot add %s: %s\n", path, strerror(errno));
    }
    close(path_fd);
    return rc;
}

static void usage(const char *prog) {
    fprintf(stderr,
            "usage: %s [--ro PATH]... [--rw PATH]... [--dev PATH]... -- COMMAND [ARG...]\n",
            prog);
}

int main(int argc, char **argv) {
    int abi = ll_create(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1) {
        fprintf(stderr, "landlock: unavailable: %s\n", strerror(errno));
        return 70;
    }

    __u64 handled = handled_rights(abi);
    struct landlock_ruleset_attr ruleset = {.handled_access_fs = handled};
    int ruleset_fd = ll_create(&ruleset, sizeof(ruleset), 0);
    if (ruleset_fd < 0) {
        fprintf(stderr, "landlock: create ruleset failed: %s\n", strerror(errno));
        return 71;
    }

    int i = 1;
    for (; i < argc; ) {
        if (strcmp(argv[i], "--") == 0) {
            ++i;
            break;
        }
        if (i + 1 >= argc) {
            usage(argv[0]);
            close(ruleset_fd);
            return 64;
        }
        __u64 allowed;
        if (strcmp(argv[i], "--ro") == 0) {
            allowed = readonly_rights();
        } else if (strcmp(argv[i], "--rw") == 0) {
            allowed = handled;
        } else if (strcmp(argv[i], "--dev") == 0) {
            allowed = device_rights();
        } else {
            usage(argv[0]);
            close(ruleset_fd);
            return 64;
        }
        if (add_path_rule(ruleset_fd, argv[i + 1], allowed) < 0) {
            close(ruleset_fd);
            return 72;
        }
        i += 2;
    }
    if (i >= argc) {
        usage(argv[0]);
        close(ruleset_fd);
        return 64;
    }

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        fprintf(stderr, "landlock: PR_SET_NO_NEW_PRIVS failed: %s\n", strerror(errno));
        close(ruleset_fd);
        return 73;
    }
    if (ll_restrict(ruleset_fd, 0) < 0) {
        fprintf(stderr, "landlock: restrict_self failed: %s\n", strerror(errno));
        close(ruleset_fd);
        return 74;
    }
    close(ruleset_fd);

    execvp(argv[i], &argv[i]);
    fprintf(stderr, "landlock: exec failed for %s: %s\n", argv[i], strerror(errno));
    return 75;
}
