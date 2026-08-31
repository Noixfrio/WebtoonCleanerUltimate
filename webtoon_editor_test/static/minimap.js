/**
 * Módulo do Mini Mapa (Navigator)
 * Responsável pelo preview e indicador de visão
 */

window.minimap = (function () {
    let miniStage, miniLayer, miniImage, viewportRect;
    const miniWidth = 200;
    const miniHeight = 150;

    function init() {
        miniStage = new Konva.Stage({
            container: 'navigator-container',
            width: miniWidth,
            height: miniHeight
        });

        miniLayer = new Konva.Layer();
        miniStage.add(miniLayer);

        viewportRect = new Konva.Rect({
            stroke: '#007bff',
            strokeWidth: 2,
            fill: 'rgba(0, 123, 255, 0.1)',
            name: 'viewport'
        });
        miniLayer.add(viewportRect);
    }

    function updateImage(img) {
        if (miniImage) miniImage.destroy();

        const scale = Math.min(miniWidth / img.width, miniHeight / img.height);

        miniImage = new Konva.Image({
            image: img,
            x: (miniWidth - img.width * scale) / 2,
            y: (miniHeight - img.height * scale) / 2,
            width: img.width * scale,
            height: img.height * scale
        });

        miniLayer.add(miniImage);
        miniImage.moveToBottom();
        update();
    }

    function update() {
        if (!miniImage || !window.stage) return;

        const mainStage = window.stage;
        const mainImg = window.imageLayer.findOne('.bg-image');
        if (!mainImg) return;

        const scaleX = miniImage.width() / mainImg.width();
        const scaleY = miniImage.height() / mainImg.height();

        // Calcular posição relativa do viewport
        const canvasArea = document.getElementById('canvas-area');

        // Posição do stage principal relativa à visualização
        const viewX = -mainStage.x() / mainStage.scaleX();
        const viewY = -mainStage.y() / mainStage.scaleY();
        const viewW = canvasArea.clientWidth / mainStage.scaleX();
        const viewH = canvasArea.clientHeight / mainStage.scaleY();

        viewportRect.setAttrs({
            x: miniImage.x() + viewX * scaleX,
            y: miniImage.y() + viewY * scaleY,
            width: viewW * scaleX,
            height: viewH * scaleY
        });

        // Limitar retângulo ao tamanho da imagem no minimapa
        viewportRect.width(Math.min(viewportRect.width(), miniImage.width()));
        viewportRect.height(Math.min(viewportRect.height(), miniImage.height()));

        miniLayer.batchDraw();
    }

    return {
        init,
        updateImage,
        update
    };
})();
