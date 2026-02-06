/**
 * 侧边栏/底边栏拖拽（事件委托）+ 消息气泡 iframe 高度自适应。
 * 不依赖 resizer 或 message-container 的挂载时机。
 */
(function () {
  "use strict";

  var messageContainerObserved = false;

  function ready(fn) {
    if (document.readyState !== "loading") {
      fn();
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  /** 侧边栏拖拽逻辑（由事件委托触发时调用） */
  function onSidebarResizerMouseDown(e) {
    e.preventDefault();
    var sidebar = document.getElementById("sidebar");
    if (!sidebar) return;
    var startX = e.clientX;
    var startW = sidebar.offsetWidth;
    var minW = 200;
    var maxW = Math.max(400, window.innerWidth * 0.5);

    function move(ev) {
      var dx = ev.clientX - startX;
      var w = Math.min(maxW, Math.max(minW, startW + dx));
      sidebar.style.width = w + "px";
    }
    function stop() {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", stop);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", stop);
  }

  /** 底边栏拖拽逻辑（由事件委托触发时调用） */
  function onBottomResizerMouseDown(e) {
    e.preventDefault();
    var inputSection = document.getElementById("input-section");
    if (!inputSection) return;
    var startY = e.clientY;
    var startH = inputSection.offsetHeight;
    var minH = 80;
    var maxH = Math.max(200, window.innerHeight * 0.5);

    function move(ev) {
      var dy = ev.clientY - startY;
      var h = Math.min(maxH, Math.max(minH, startH - dy));
      inputSection.style.height = h + "px";
    }
    function stop() {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", stop);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }
    document.body.style.cursor = "row-resize";
    document.body.style.userSelect = "none";
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", stop);
  }

  /** 一次绑定：通过事件委托处理侧边/底边 resizer 的 mousedown（捕获阶段避免被拦截） */
  function setupResizerDelegation() {
    document.body.addEventListener("mousedown", function (e) {
      var target = e.target;
      if (target.id === "sidebar-resizer" || (target.closest && target.closest("#sidebar-resizer"))) {
        onSidebarResizerMouseDown(e);
        return;
      }
      if (target.id === "bottom-resizer" || (target.closest && target.closest("#bottom-resizer"))) {
        onBottomResizerMouseDown(e);
      }
    }, true);
  }

  /** 将消息区内的 iframe（Markdown 渲染）按内容高度自适应。 */
  function resizeMessageIframes() {
    var container = document.getElementById("message-container");
    if (!container) return;
    var iframes = container.querySelectorAll("iframe.message-content-iframe");
    iframes.forEach(function (iframe) {
      try {
        var doc = iframe.contentDocument;
        if (doc && doc.body) {
          var h = Math.max(24, doc.body.scrollHeight + 2);
          iframe.style.height = h + "px";
        }
      } catch (err) {}
    });
  }

  /** 对 #message-container 挂 MutationObserver，仅执行一次（延迟挂载时调用）。 */
  function observeMessageContainer() {
    if (messageContainerObserved) return;
    var container = document.getElementById("message-container");
    if (!container) return;
    messageContainerObserved = true;
    resizeMessageIframes();
    var observer = new MutationObserver(function () {
      resizeMessageIframes();
      setTimeout(resizeMessageIframes, 100);
      setTimeout(resizeMessageIframes, 300);
      setTimeout(resizeMessageIframes, 600);
    });
    observer.observe(container, { childList: true, subtree: true });
  }

  ready(function () {
    setupResizerDelegation();
    observeMessageContainer();

    var appContent = document.getElementById("_dash-app-content");
    var observeTarget = appContent || document.body;
    var observer = new MutationObserver(function () {
      observeMessageContainer();
    });
    observer.observe(observeTarget, { childList: true, subtree: true });

    setTimeout(resizeMessageIframes, 500);
    setTimeout(resizeMessageIframes, 1200);
  });
})();
