// Generado por tai-api: este fichero lo reescribe `tai-api generate`.
// El modelo de datos en el Swagger: cada diagrama ER se enseña en su sección y, al pulsarlo, se
// abre a pantalla completa para ampliarlo (rueda o botones), moverlo (arrastrar) y cerrarlo (Esc).
(function () {
  "use strict";

  var MIN = 0.1, MAX = 8, STEP = 1.25;

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { node.appendChild(c); });
    return node;
  }

  // ── El visor ──────────────────────────────────────────────────────────────

  function openViewer(src, title) {
    var img = el("img", { src: src, alt: "Diagrama ER de " + title, draggable: "false" });
    var zoomLabel = el("span", { "class": "tai-viewer-zoom", text: "" });
    var stage = el("div", { "class": "tai-viewer-stage" }, [img]);
    var btn = function (label, name) { return el("button", { type: "button", title: name, "aria-label": name, text: label }); };
    var out = btn("−", "Reducir"), into = btn("+", "Ampliar"), fit = btn("Ajustar", "Ajustar a la pantalla"),
        real = btn("100%", "Tamaño real"), close = btn("✕", "Cerrar");
    var tab = el("a", { href: src, target: "_blank", rel: "noopener", text: "Abrir en pestaña" });
    var viewer = el("div", { "class": "tai-viewer", role: "dialog", "aria-modal": "true", "aria-label": title }, [
      el("div", { "class": "tai-viewer-bar" }, [el("strong", { text: title }), out, zoomLabel, into, fit, real, tab, close]),
      stage,
      el("div", { "class": "tai-viewer-hint", text: "Rueda para ampliar · arrastra para moverte · doble clic para acercar · Esc para cerrar" }),
    ]);

    var scale = 1, x = 0, y = 0, naturalW = 0, naturalH = 0;

    function paint() {
      // Se cambia el tamaño, no un `transform: scale`: así el SVG se vuelve a dibujar nítido.
      img.style.width = naturalW * scale + "px";
      img.style.height = naturalH * scale + "px";
      img.style.transform = "translate(" + x + "px," + y + "px)";
      zoomLabel.textContent = Math.round(scale * 100) + "%";
    }

    function zoomAt(factor, cx, cy) {
      var next = Math.min(MAX, Math.max(MIN, scale * factor));
      var rect = stage.getBoundingClientRect();
      var px = (cx === undefined ? rect.width / 2 : cx - rect.left), py = (cy === undefined ? rect.height / 2 : cy - rect.top);
      x = px - (px - x) * (next / scale);
      y = py - (py - y) * (next / scale);
      scale = next;
      paint();
    }

    function fitToStage() {
      var rect = stage.getBoundingClientRect();
      scale = Math.min(1, (rect.width - 48) / naturalW, (rect.height - 48) / naturalH);
      x = (rect.width - naturalW * scale) / 2;
      y = (rect.height - naturalH * scale) / 2;
      paint();
    }

    function actualSize() {
      var rect = stage.getBoundingClientRect();
      scale = 1; x = (rect.width - naturalW) / 2; y = 24;
      paint();
    }

    img.addEventListener("load", function () {
      naturalW = img.naturalWidth || 1200;
      naturalH = img.naturalHeight || 800;
      fitToStage();
    });

    stage.addEventListener("wheel", function (e) {
      e.preventDefault();
      zoomAt(e.deltaY < 0 ? 1.12 : 1 / 1.12, e.clientX, e.clientY);
    }, { passive: false });

    var drag = null;
    stage.addEventListener("pointerdown", function (e) {
      drag = { px: e.clientX, py: e.clientY, x: x, y: y };
      stage.setPointerCapture(e.pointerId);
      stage.classList.add("dragging");
    });
    stage.addEventListener("pointermove", function (e) {
      if (!drag) return;
      x = drag.x + e.clientX - drag.px;
      y = drag.y + e.clientY - drag.py;
      paint();
    });
    function endDrag() { drag = null; stage.classList.remove("dragging"); }
    stage.addEventListener("pointerup", endDrag);
    stage.addEventListener("pointercancel", endDrag);
    stage.addEventListener("dblclick", function (e) { zoomAt(STEP * STEP, e.clientX, e.clientY); });

    out.addEventListener("click", function () { zoomAt(1 / STEP); });
    into.addEventListener("click", function () { zoomAt(STEP); });
    fit.addEventListener("click", fitToStage);
    real.addEventListener("click", actualSize);

    var previousOverflow = document.body.style.overflow;
    function onKey(e) {
      if (e.key === "Escape") closeViewer();
      else if (e.key === "+" || e.key === "=") zoomAt(STEP);
      else if (e.key === "-") zoomAt(1 / STEP);
      else if (e.key === "0") fitToStage();
    }
    function closeViewer() {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
      viewer.remove();
    }
    close.addEventListener("click", closeViewer);
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    document.body.appendChild(viewer);
    close.focus();
  }

  // ── La sección del modelo de datos ────────────────────────────────────────

  function section(diagrams) {
    var items = diagrams.map(function (d) {
      var body;
      if (d.svg) {
        var thumb = el("button", { type: "button", "class": "tai-thumb", title: "Ampliar el diagrama de " + d.schema },
          [el("img", { src: d.svg, alt: "Diagrama ER de " + d.schema, loading: "lazy" })]);
        thumb.addEventListener("click", function () { openViewer(d.svg, "Modelo de datos · " + d.schema); });
        body = thumb;
      } else {
        body = el("p", {}, [el("a", { href: d.page, text: "Ver el diagrama interactivo de " + d.schema })]);
      }
      return el("details", diagrams.length === 1 ? { open: "" } : {}, [el("summary", { text: d.schema }), body]);
    });
    return el("section", { "class": "tai-model" }, [
      el("h3", { text: "Modelo de datos" }),
      el("p", { text: "Pulsa un diagrama para ampliarlo." }),
    ].concat(items));
  }

  // Swagger pinta la cabecera cuando ha leído el openapi.json: se espera a que exista.
  function injectDiagrams(diagrams) {
    if (!diagrams || !diagrams.length) return;
    var tries = 0;
    (function attempt() {
      var info = document.querySelector("#swagger-ui .information-container .info");
      if (info && !document.querySelector(".tai-model")) {
        info.parentNode.insertBefore(section(diagrams), info.nextSibling);
      } else if (!info && tries++ < 100) {
        setTimeout(attempt, 100);
      }
    })();
  }

  window.taiDocs = { openViewer: openViewer, injectDiagrams: injectDiagrams };
})();
