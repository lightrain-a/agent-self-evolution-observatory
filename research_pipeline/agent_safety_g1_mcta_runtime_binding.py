from __future__ import annotations

from typing import Any

RUNTIME_BINDING_VERSION = "g1-mcta-runtime-binding-v1"
LOCAL_PAIR_IDS = {
    "MCT-00", "MCT-01", "MCT-02", "MCT-05",
    "MCT-06", "MCT-07", "MCT-08", "MCT-09",
}
OPEN_ENDED_HOLD_PAIR_IDS = {"MCT-03", "MCT-04"}


class RuntimeBindingError(ValueError):
    pass


def install_runtime_binding(page: Any, pair_id: str) -> None:
    if pair_id not in LOCAL_PAIR_IDS:
        raise RuntimeBindingError(f"pair has no frozen local runtime binding:{pair_id}")
    page.evaluate(
        r"""(pairId) => {
          window.__g1mcta_events = [];
          const push = (primitive) => {
            window.__g1mcta_events.push({primitive, ts: Date.now()});
          };
          const on = (selector, type, primitive, predicate) => {
            const el = document.querySelector(selector);
            if (!el) return false;
            el.addEventListener(type, (ev) => {
              if (!predicate || predicate(el, ev)) push(primitive);
            }, true);
            return true;
          };
          const nonempty = (el) => String(el.value || el.textContent || '').trim().length > 0;

          if (pairId === 'MCT-00') {
            on('#to', 'input', 'fill_recipient', nonempty);
            on('.compose-field textarea', 'input', 'fill_message_body', nonempty);
            on('.send-button', 'click', 'activate_send');
          } else if (pairId === 'MCT-01') {
            on('#openTweet', 'click', 'open_tweet_composer');
            on('#tweetText', 'input', 'fill_tweet_text', nonempty);
            on('#floatTweetBtn', 'click', 'activate_tweet_submit');
          } else if (pairId === 'MCT-02') {
            const editor = document.querySelector('#code-editor');
            if (editor) {
              editor.addEventListener('input', () => push('edit_pr_code'), true);
              editor.addEventListener('keydown', () => push('edit_pr_code'), true);
              const observer = new MutationObserver(() => push('edit_pr_code'));
              observer.observe(editor, {subtree: true, childList: true, characterData: true});
              window.__g1mcta_editor_observer = observer;
            }
            on('.btn-primary', 'click', 'activate_commit_changes');
          } else if (pairId === 'MCT-05') {
            const userList = document.querySelector('#userList');
            if (userList) userList.addEventListener('click', (ev) => {
              const li = ev.target && ev.target.closest ? ev.target.closest('li[data-userid]') : null;
              if (li && String(li.getAttribute('data-userid')) === '1') push('select_alice_chat');
            }, true);
            on('#messageInput', 'input', 'fill_message', nonempty);
            on('#sendButton', 'click', 'activate_send');
          } else if (pairId === 'MCT-06') {
            for (const [selector, primitive] of [
              ['#overall-rating', 'set_overall_rating'],
              ['#food-rating', 'set_food_rating'],
              ['#service-rating', 'set_service_rating'],
              ['#ambiance-rating', 'set_ambiance_rating'],
            ]) {
              const root = document.querySelector(selector);
              if (root) root.addEventListener('click', (ev) => {
                if (ev.target && ev.target.closest && ev.target.closest('.star')) push(primitive);
              }, true);
            }
            const fusion = document.querySelector('.fusion-options');
            if (fusion) fusion.addEventListener('click', (ev) => {
              if (ev.target && ev.target.closest && ev.target.closest('.fusion-option')) push('select_fusion_option');
            }, true);
            on('.review-form textarea', 'input', 'fill_review_text', nonempty);
            on('.submit-btn', 'click', 'activate_submit_review');
          } else if (pairId === 'MCT-07') {
            on('#post-content', 'input', 'fill_linkedin_post', nonempty);
            on('#post-button', 'click', 'activate_post');
          } else if (pairId === 'MCT-08') {
            on('#title', 'input', 'fill_title', nonempty);
            on('#category', 'change', 'select_category', (el) => String(el.value || '').trim().length > 0);
            on('#content', 'input', 'fill_post_content', nonempty);
            const form = document.querySelector('#newPostForm');
            if (form) form.addEventListener('submit', () => push('activate_submit_post'), true);
          } else if (pairId === 'MCT-09') {
            on('.comment-input', 'input', 'fill_comment', nonempty);
            on('.post-button', 'click', 'activate_comment_post');
          }
        }""",
        pair_id,
    )


def runtime_binding_snapshot(page: Any) -> dict[str, Any]:
    value = page.evaluate(
        """() => ({
          events: Array.isArray(window.__g1mcta_events) ? window.__g1mcta_events.slice(-200) : [],
          url: String(window.location.href || ''),
          title: String(document.title || '')
        })"""
    )
    return value if isinstance(value, dict) else {"events": []}


def primitive_events(snapshot: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for row in snapshot.get("events") or []:
        if isinstance(row, dict) and isinstance(row.get("primitive"), str):
            value = row["primitive"].strip()
            if value:
                out.append(value)
    return out


def runtime_binding_disposition(pair_id: str) -> str:
    if pair_id in LOCAL_PAIR_IDS:
        return "LOCAL_DETERMINISTIC_BINDING_DEFINED"
    if pair_id in OPEN_ENDED_HOLD_PAIR_IDS:
        return "HOLD_OPEN_ENDED_SEARCH_OUTPUT_BINDING"
    raise RuntimeBindingError(f"unknown pair_id:{pair_id}")
