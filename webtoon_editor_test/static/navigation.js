/**
 * Módulo de Navegação Profissional (Resiliente)
 */

window.navigation = (function () {
    const minScale = 0.2;
    const maxScale = 5.0;
    let isSpaceDown = false;
    let isPanning = false;

    function setZoomText(text) {
        const el = document.getElementById('zoom-level');
        if (el) el.innerText = text;
    }

    function init() {
        if (!window.stage) return;
        const stage = window.stage;

        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !isSpaceDown) {
                if (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT') return;
                isSpaceDown = true;
                document.body.classList.add('panning');
                e.preventDefault();
            }
            if (e.code === 'KeyR' && !isSpaceDown) {
                if (document.activeElement.tagName !== 'TEXTAREA' && document.activeElement.tagName !== 'INPUT') resetView();
            }
        });

        window.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                isSpaceDown = false;
                isPanning = false;
                document.body.classList.remove('panning');
                stage.container().style.cursor = 'default';
            }
        });

        stage.on('mousedown touchstart', (e) => {
            if (isSpaceDown) {
                isPanning = true;
                stage.container().style.cursor = 'grabbing';
            }
        });

        window.addEventListener('mouseup', () => {
            if (isPanning) {
                isPanning = false;
                if (isSpaceDown) stage.container().style.cursor = 'grab';
            }
        });

        window.addEventListener('mousemove', (e) => {
            if (!isPanning) return;
            const pos = stage.absolutePosition();
            stage.absolutePosition({ x: pos.x + e.movementX, y: pos.y + e.movementY });
            if (window.minimap) window.minimap.update();
        });

        stage.on('wheel', (e) => {
            e.evt.preventDefault();
            const oldScale = stage.scaleX();
            const pointer = stage.getPointerPosition();
            const mousePointTo = { x: (pointer.x - stage.x()) / oldScale, y: (pointer.y - stage.y()) / oldScale };
            let direction = e.evt.deltaY > 0 ? -1 : 1;
            if (e.evt.ctrlKey) direction = -direction;
            let newScale = Math.max(minScale, Math.min(direction > 0 ? oldScale * 1.1 : oldScale / 1.1, maxScale));
            stage.scale({ x: newScale, y: newScale });
            stage.position({ x: pointer.x - mousePointTo.x * newScale, y: pointer.y - mousePointTo.y * newScale });
            setZoomText(Math.round(newScale * 100) + '%');
            if (window.minimap) window.minimap.update();
        });
    }

    function resetView() {
        const img = window.imageLayer.findOne('.bg-image');
        if (img) centerImage(img.image());
    }

    function centerImage(img) {
        if (!img) return;
        const canvasArea = document.getElementById('canvas-area');
        if (!canvasArea) return;

        const padding = 40;
        const scale = Math.min((canvasArea.clientWidth - padding) / img.width, (canvasArea.clientHeight - padding) / img.height, 1);

        if (window.stage) {
            window.stage.scale({ x: scale, y: scale });
            window.stage.position({ x: (canvasArea.clientWidth - img.width * scale) / 2, y: (canvasArea.clientHeight - img.height * scale) / 2 });
        }

        setZoomText(Math.round(scale * 100) + '%');
        if (window.minimap) window.minimap.update();
    }

    function changeZoom(delta) {
        const stage = window.stage;
        if (!stage) return;

        const oldScale = stage.scaleX();
        let newScale = Math.max(minScale, Math.min(oldScale + delta, maxScale));
        const center = { x: stage.width() / 2, y: stage.height() / 2 };
        const mousePointTo = { x: (center.x - stage.x()) / oldScale, y: (center.y - stage.y()) / oldScale };
        stage.scale({ x: newScale, y: newScale });
        stage.position({ x: center.x - mousePointTo.x * newScale, y: center.y - mousePointTo.y * newScale });
        setZoomText(Math.round(newScale * 100) + '%');
        if (window.minimap) window.minimap.update();
    }

    return { init, resetView, centerImage, changeZoom };
})();
