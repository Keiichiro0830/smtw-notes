/* FORGE — ヘッダー・リビール・ホームの状態表示（依存なし） */
(function () {
  var d = document, root = d.documentElement;
  root.classList.add("js");

  /* モバイルメニュー */
  var btn = d.querySelector(".fg-menu"), nav = d.querySelector(".fg-nav");
  if (btn && nav) {
    var set = function (open) { nav.setAttribute("data-open", String(open)); btn.setAttribute("aria-expanded", String(open)); };
    btn.addEventListener("click", function () { set(nav.getAttribute("data-open") !== "true"); });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape") set(false); });
    nav.addEventListener("click", function (e) { if (e.target.tagName === "A") set(false); });
  }

  /* 日英兼用ページの言語切替 */
  var sw = d.querySelector("[data-inpage-lang]");
  if (sw) {
    var apply = function (l) {
      root.lang = l;
      sw.textContent = l === "ja" ? "EN" : "JA";
      sw.setAttribute("aria-label", l === "ja" ? "English" : "日本語");
      [].forEach.call(d.querySelectorAll("a[data-href-ja]"), function (a) { a.setAttribute("href", a.getAttribute("data-href-" + l)); });
      try { localStorage.setItem("smtw_lang", l); } catch (e) {}
    };
    var saved = null;
    try { saved = localStorage.getItem("smtw_lang"); } catch (e) {}
    apply(saved === "en" || saved === "ja" ? saved : ((navigator.language || "").indexOf("ja") === 0 ? "ja" : "en"));
    sw.addEventListener("click", function () { apply(root.lang === "ja" ? "en" : "ja"); });
  }

  /* スクロール・リビール（IntersectionObserver が無い／発火しなくても 2.5 秒後には必ず表示） */
  var items = [].slice.call(d.querySelectorAll(".fg-reveal"));
  var show = function (el) { el.classList.add("is-in"); };
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { show(e.target); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.05 });
    items.forEach(function (el) { io.observe(el); });
    setTimeout(function () { items.forEach(show); }, 2500);
  } else { items.forEach(show); }

  /* 読み進みバー */
  var bar = d.querySelector(".fg-progress");
  if (bar) {
    var tick = false;
    var upd = function () {
      var h = root.scrollHeight - root.clientHeight;
      bar.style.setProperty("--p", h > 0 ? Math.min(1, Math.max(0, (window.pageYOffset || root.scrollTop) / h)).toFixed(4) : 0);
      tick = false;
    };
    window.addEventListener("scroll", function () { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive: true });
    upd();
  }

  /* タイルのスポットライト */
  [].forEach.call(d.querySelectorAll(".fg-tile"), function (t) {
    t.addEventListener("pointermove", function (e) {
      var r = t.getBoundingClientRect();
      t.style.setProperty("--tx", (e.clientX - r.left) + "px");
      t.style.setProperty("--ty", (e.clientY - r.top) + "px");
    });
  });

  /* ヒーローの光（ポインタ追従） */
  var hero = d.querySelector(".fg-hero");
  if (hero && window.matchMedia && matchMedia("(pointer:fine)").matches && !matchMedia("(prefers-reduced-motion:reduce)").matches) {
    hero.addEventListener("pointermove", function (e) {
      var r = hero.getBoundingClientRect();
      hero.style.setProperty("--mx", ((e.clientX - r.left) / r.width * 100).toFixed(1) + "%");
      hero.style.setProperty("--my", ((e.clientY - r.top) / r.height * 100).toFixed(1) + "%");
    });
  }


  /* ライトボックス: data-zoom を持つ画像をクリックで拡大・保存 */
  var zoomables = d.querySelectorAll("[data-zoom]");
  if (zoomables.length) {
    var lb = d.createElement("div");
    lb.className = "fg-lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true");
    lb.innerHTML = '<img alt=""><div class="cap"></div><div class="bar"><a download href="#"><span class="ja">保存</span><span class="en">Save</span></a><button type="button"><span class="ja">閉じる</span><span class="en">Close</span></button></div>';
    d.body.appendChild(lb);
    var lbImg = lb.querySelector("img"), lbDl = lb.querySelector("a"), lbCap = lb.querySelector(".cap");
    var closeLb = function () { lb.classList.remove("is-open"); lbImg.removeAttribute("src"); };
    d.addEventListener("click", function (e) {
      var t = e.target;
      if (t.matches && t.matches("img[data-zoom]")) {
        lbImg.src = t.currentSrc || t.src; lbImg.alt = t.alt || ""; lbDl.href = lbImg.src;
        lbDl.setAttribute("download", t.getAttribute("data-name") || "image.jpg");
        var fig = t.closest("figure"), fc = fig && fig.querySelector("figcaption");
        lbCap.innerHTML = fc ? fc.innerHTML : "";
        lb.classList.add("is-open");
      } else if (t === lb || (t.closest && t.closest(".fg-lb button"))) { closeLb(); }
    });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLb(); });
  }

  /* ホーム: 開催記録の状態を「今日の日付」から導く（「次回」の書きっぱなしを防ぐ） */
  var rows = [].slice.call(d.querySelectorAll(".fg-ledger li[data-date]"));
  var status = d.getElementById("fg-status");
  if (rows.length) {
    var now = new Date(), pad = function (n) { return ("0" + n).slice(-2); };
    var today = now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate());
    var lang = root.lang === "en" ? "en" : "ja";
    var dt = function (r) { return r.getAttribute("data-date"); };
    var byDate = rows.slice().sort(function (a, b) { return dt(a) < dt(b) ? -1 : 1; });
    var past = byDate.filter(function (r) { return dt(r) <= today; });
    var future = byDate.filter(function (r) { return dt(r) > today; });
    var dated = future.filter(function (r) { return dt(r).indexOf("9999") !== 0; });
    var latest = past[past.length - 1], next = dated[0], tbd = future[future.length - 1];
    rows.forEach(function (r) { r.classList.remove("is-latest", "is-next"); });
    if (latest) latest.classList.add("is-latest");
    var focus = next || tbd;
    if (focus) focus.classList.add("is-next");
    if (status) {
      var label = function (r) { return r.getAttribute("data-label-" + lang) || ""; };
      var txt, tag;
      if (next) {
        tag = "NEXT";
        txt = (lang === "ja" ? "次回: " : "Next: ") + label(next) + " (" + dt(next).replace(/-/g, ".") + ")";
      } else if (latest) {
        tag = "LATEST";
        txt = status.getAttribute("data-latest-" + lang) || label(latest);
      }
      if (txt) { status.querySelector(".st").textContent = txt; status.querySelector("b").textContent = tag; }
    }
  }
})();
