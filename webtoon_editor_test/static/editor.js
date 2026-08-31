const editor = (() => {
    let stage, layer, imageLayer, transformer, selectionRect, lastSelectionBox;
    let isOCRModeActive = false; // Estado do Modo OCR (v28.1)

    return {
        init: (containerId) => {
            const container = document.getElementById(containerId);
            if (!container) return;

            stage = new Konva.Stage({
                container: containerId,
                width: container.offsetWidth || window.innerWidth - 350,
                height: container.offsetHeight || window.innerHeight
            });
            layer = new Konva.Layer();
            imageLayer = new Konva.Layer();
            stage.add(imageLayer);
            stage.add(layer);

            transformer = new Konva.Transformer({
                nodes: [],
                rotateEnabled: true,
                padding: 10,
                enabledAnchors: ['top-left', 'top-right', 'bottom-left', 'bottom-right']
            });
            layer.add(transformer);

            selectionRect = new Konva.Rect({
                fill: 'rgba(0,0,255,0.2)',
                stroke: '#007bff',
                strokeWidth: 1,
                visible: false
            });
            layer.add(selectionRect);

            window.stage = stage;
            window.layer = layer;
            window.imageLayer = imageLayer;
            window.transformer = transformer;

            let x1, y1;
            stage.on('mousedown touchstart', (e) => {
                // MODO OCR v28.1: Se estiver desligado, não faz seleção de área
                if (!isOCRModeActive) return;

                // SE ESTIVERMOS NO MODO PAN (SPACEBAR), NÃO FAZ SELEÇÃO (v27.8 Fix)
                if (document.body.classList.contains('panning')) return;

                const isBg = e.target === stage || (imageLayer.findOne('Image') && e.target === imageLayer.findOne('Image'));
                if (!isBg) return;

                // Capturar posição relativa ao palco transformado (v27.8 Fix)
                const transform = stage.getAbsoluteTransform().copy().invert();
                const pos = transform.point(stage.getPointerPosition());

                x1 = pos.x;
                y1 = pos.y;

                selectionRect.visible(true);
                selectionRect.width(0);
                selectionRect.height(0);
                selectionRect.x(x1);
                selectionRect.y(y1);
                layer.draw();
            });

            stage.on('mousemove touchmove', (e) => {
                if (!selectionRect.visible()) return;

                const transform = stage.getAbsoluteTransform().copy().invert();
                const pos = transform.point(stage.getPointerPosition());

                selectionRect.setAttrs({
                    x: Math.min(x1, pos.x),
                    y: Math.min(y1, pos.y),
                    width: Math.abs(pos.x - x1),
                    height: Math.abs(pos.y - y1),
                });
                layer.draw();
            });

            stage.on('mouseup touchend', (e) => {
                if (!selectionRect.visible()) return;

                const box = {
                    x: selectionRect.x(),
                    y: selectionRect.y(),
                    width: selectionRect.width(),
                    height: selectionRect.height()
                };

                if (box.width > 5 && box.height > 5) {
                    lastSelectionBox = box;

                    // Salvar também em coordenadas de TELA para captura de imagem (v27.9 Fix)
                    const pos = selectionRect.getAbsolutePosition();
                    const scale = stage.scaleX();
                    lastSelectionBox.screen = {
                        x: pos.x,
                        y: pos.y,
                        width: box.width * scale,
                        height: box.height * scale
                    };

                    console.log("Área capturada (Inner):", box);
                }

                selectionRect.visible(false);
                layer.draw();
            });

            stage.on('click tap', (e) => {
                // Se clicou no fundo (Stage ou Imagem de Fundo), deseleciona
                const isBg = e.target === stage || (imageLayer.findOne('Image') && e.target === imageLayer.findOne('Image'));
                if (isBg) {
                    transformer.nodes([]);
                    layer.draw();
                    return;
                }

                // [FIX] v29.2: Procura o nó pai que está diretamente no layer (pode ser o target ou um Group ancestral)
                // Isso é essencial para selecionar SFX (Grupos) ou objetos restaurados via JSON
                let targetNode = e.target;
                while (targetNode && targetNode.getParent() !== layer) {
                    targetNode = targetNode.getParent();
                    if (!targetNode) break;
                }

                if (targetNode && targetNode !== transformer && targetNode !== selectionRect) {
                    transformer.nodes([targetNode]);
                    layer.draw();
                    if (typeof updateSidebar === 'function') updateSidebar(targetNode);
                }
            });

            window.addEventListener('resize', () => {
                if (stage && container) {
                    stage.width(container.offsetWidth);
                    stage.height(container.offsetHeight);
                    stage.draw();
                }
            });
        },

        loadImage: (src) => {
            Konva.Image.fromURL(src, (img) => {
                imageLayer.destroyChildren();
                img.setAttrs({
                    x: 0, y: 0,
                    name: 'bg-image'
                });
                imageLayer.add(img);
                imageLayer.draw();

                if (window.navigation) {
                    window.navigation.centerImage(img.image());
                } else {
                    stage.scale({ x: 1, y: 1 });
                    stage.position({ x: 0, y: 0 });
                }

                if (window.minimap) {
                    window.minimap.updateImage(img.image());
                }

                stage.batchDraw();
            });
        },

        addText: (content = "Novo Texto") => {
            const transform = stage.getAbsoluteTransform().copy().invert();
            const center = transform.point({ x: stage.width() / 2, y: stage.height() / 2 });

            const text = new Konva.Text({
                x: center.x - 50, y: center.y - 20,
                text: content,
                fontSize: 40,
                fontFamily: 'Arial',
                fill: '#000000',
                draggable: true,
                name: 'text-node'
            });
            layer.add(text);
            transformer.nodes([text]);
            layer.draw();
            updateSidebar(text);
        },

        loadRemoteImage: (base64) => {
            // Reutiliza a lógica de carregamento principal (Konva.Image.fromURL)
            if (editor && editor.loadImage) {
                editor.loadImage(base64);
                console.log("[EDITOR] Imagem remota carregada via Editor.loadImage.");
            } else {
                // Fallback caso o objeto editor não esteja totalmente exposto
                const img = new Image();
                img.onload = () => {
                    Konva.Image.fromURL(base64, (kImg) => {
                        imageLayer.destroyChildren();
                        imageLayer.add(kImg);
                        imageLayer.draw();
                        if (window.navigation) window.navigation.centerImage(kImg.image());
                    });
                };
                img.src = base64;
            }
        },

        addNewSFX: async () => {
            if (window.styleExtract) window.styleExtract.renderSFX();
        },

        updateSelectedText: () => {
            try {
                const node = transformer.nodes()[0];
                if (!node) return;

                const contentEl = document.getElementById('sidebar-text-content');
                if (!contentEl) return;

                const content = contentEl.value;
                const fSize = document.getElementById('font-size').value * 1;
                const fFamily = document.getElementById('font-family').value;
                const fWeight = document.getElementById('font-weight').value;
                const fColor = document.getElementById('text-color').value;
                const sColor = document.getElementById('stroke-color').value;
                const sWidth = document.getElementById('stroke-width').value * 1;
                const lSpacing = document.getElementById('letter-spacing').value * 1;
                const lHeight = document.getElementById('line-height').value * 1;
                const scX = document.getElementById('scale-x').value * 1;
                const skX = document.getElementById('skew-x').value * 1;
                const skY = document.getElementById('skew-y').value * 1;
                const shadowAtiva = document.getElementById('text-shadow').checked;
                const sBlur = document.getElementById('shadow-blur').value * 1;
                const sOffset = document.getElementById('shadow-offset').value * 1;
                const sColorVal = document.getElementById('shadow-color').value;

                if (node.text || node.getClassName() === 'Text') {
                    node.setAttrs({
                        text: content,
                        fontSize: fSize,
                        fontFamily: fFamily,
                        fontStyle: fWeight,
                        fill: fColor,
                        stroke: sColor,
                        strokeWidth: sWidth,
                        letterSpacing: lSpacing,
                        lineHeight: lHeight,
                        scaleX: scX,
                        skewX: skX,
                        skewY: skY,
                        shadowEnabled: shadowAtiva,
                        shadowColor: sColorVal,
                        shadowBlur: sBlur,
                        shadowOffset: { x: sOffset, y: sOffset },
                        shadowOpacity: shadowAtiva ? 1 : 0
                    });
                    layer.batchDraw();
                } else if (node.getClassName() === 'Image') {
                    // Para SFX (Imagem), aplicamos apenas atributos de geometria Live
                    node.setAttrs({
                        scaleX: scX,
                        skewX: skX,
                        skewY: skY
                    });
                    layer.batchDraw();
                }
            } catch (err) {
                console.warn("DNA: Erro silencioso no updateSelectedText:", err);
            }
        },

        deleteSelected: () => {
            const nodes = transformer.nodes();
            nodes.forEach(n => n.destroy());
            transformer.nodes([]);
            layer.draw();
        },

        centerSelectedText: () => {
            const node = transformer.nodes()[0];
            if (!node) return;
            const transform = stage.getAbsoluteTransform().copy().invert();
            const center = transform.point({ x: stage.width() / 2, y: stage.height() / 2 });
            node.x(center.x - node.width() / 2);
            node.y(center.y - node.height() / 2);
            layer.draw();
        },

        resetGeometry: () => {
            const node = transformer.nodes()[0];
            if (!node) return;
            node.scaleX(1); node.scaleY(1);
            node.rotation(0); node.skewX(0); node.skewY(0);
            layer.draw();
        },

        exportImage: (autoDownload = true) => {
            const bgNode = stage.findOne('.bg-image');
            if (!bgNode) return alert("Nenhuma imagem carregada.");

            // Salvar estado atual para restaurar depois
            const oldPos = stage.position();
            const oldScale = stage.scale();
            const oldNodes = transformer.nodes();

            // 1. Limpar ferramentas e resetar palco para escala 1:1
            transformer.nodes([]);
            stage.position({ x: 0, y: 0 });
            stage.scale({ x: 1, y: 1 });
            stage.draw();

            // 2. Exportar apenas a área da imagem original
            const dataURL = stage.toDataURL({
                x: bgNode.x(),
                y: bgNode.y(),
                width: bgNode.width(),
                height: bgNode.height(),
                pixelRatio: 1 // Mantém a resolução original da importação
            });

            // 3. Restaurar o editor ao estado anterior
            stage.position(oldPos);
            stage.scale(oldScale);
            transformer.nodes(oldNodes);
            stage.draw();

            // Apenas faz o download se solicitado (Evita o popup indesejado no 'Salvar e Voltar')
            if (autoDownload) {
                const link = document.createElement('a');
                link.download = 'manhua_editada.png';
                link.href = dataURL;
                link.click();
            }

            // Sincronia v29.0: Inclui o Estado Konva (JSON) para permitir RE-EDIÇÃO futuramente
            if (window.opener) {
                try {
                    const urlParams = new URLSearchParams(window.location.search);
                    const index = urlParams.get('index');

                    // Exportamos o JSON da camada principal (textos e SFX)
                    const konvaState = layer.toJSON();

                    window.opener.postMessage({
                        type: "EDITOR_RESULT",
                        index: index,
                        base64: dataURL,
                        konvaState: konvaState
                    }, "*");
                    console.log("[INTEGRAÇÃO] Resultado e Estado (JSON) enviados para o projeto principal.");
                } catch (e) {
                    console.warn("[INTEGRAÇÃO] Falha ao enviar postMessage:", e);
                }
            }
        },

        syncAndClose: () => {
            const bgNode = stage.findOne('.bg-image');
            if (!bgNode) {
                const targetWindow = window.opener || window.parent;
                if (targetWindow && targetWindow !== window) {
                    targetWindow.postMessage({ type: "CLOSE_EDITOR" }, "*");
                } else {
                    window.location.href = "http://localhost:5000";
                }
                return;
            }

            // Exporta (v29.1: Agora desativamos o download automático para evitar o popup chato)
            editor.exportImage(false);

            // Pequeno delay para garantir o envio antes de fechar
            setTimeout(() => {
                const targetWindow = window.opener || window.parent;
                if (targetWindow && targetWindow !== window) {
                    targetWindow.postMessage({ type: "CLOSE_EDITOR" }, "*");
                } else {
                    window.location.href = "http://localhost:5000";
                }
            }, 600);
        },

        loadProject: (json) => {
            if (!json) return;
            try {
                // Limpar camada atual
                layer.destroyChildren();

                // Recriar Transformer e SelectionRect (pois o layer.destroy limpou tudo)
                transformer = new Konva.Transformer({
                    nodes: [],
                    rotateEnabled: true,
                    padding: 10,
                    enabledAnchors: ['top-left', 'top-right', 'bottom-left', 'bottom-right']
                });
                layer.add(transformer);
                window.transformer = transformer;

                selectionRect = new Konva.Rect({
                    fill: 'rgba(0,0,255,0.2)',
                    stroke: '#007bff',
                    strokeWidth: 1,
                    visible: false
                });
                layer.add(selectionRect);
                window.selectionRect = selectionRect;

                // Carregar nós do JSON
                const tempLayer = Konva.Node.create(json);
                tempLayer.getChildren().forEach(node => {
                    // Evitar trazer o transformer/rect antigo se o JSON os capturou
                    if (node.getClassName() !== 'Transformer' && node.id() !== 'selectionRect') {
                        layer.add(node);
                    }
                });
                layer.draw();
                console.log("[EDITOR] Projeto (Konva JSON) carregado com sucesso.");
            } catch (e) {
                console.error("[EDITOR] Erro ao carregar projeto JSON:", e);
            }
        },

        updateHexLabels: () => {
            const ids = ['text-color', 'grad-color-1', 'grad-color-2', 'stroke-color', 'shadow-color'];
            ids.forEach(id => {
                const el = document.getElementById(id);
                const display = document.getElementById(`hex-${id}`);
                if (el && display) display.innerText = el.value.toUpperCase();
            });
        },

        toggleOCRMode: () => {
            isOCRModeActive = !isOCRModeActive;
            const btn = document.getElementById('btn-ocr-toggle');
            const extractBtn = document.getElementById('btn-extract-ocr');

            if (isOCRModeActive) {
                btn.innerText = "ON";
                btn.style.background = "#27ae60"; // Verde Sucesso
                btn.style.borderColor = "#2ecc71";
                if (extractBtn) {
                    extractBtn.disabled = false;
                    extractBtn.style.opacity = "1";
                }
            } else {
                btn.innerText = "OFF";
                btn.style.background = "#2c3e50"; // Escuro Padrão
                btn.style.borderColor = "#34495e";
                if (extractBtn) {
                    extractBtn.disabled = true;
                    extractBtn.style.opacity = "0.5";
                }
                selectionRect.visible(false);
                layer.draw();
            }
        },

        extractTextFromScreen: async () => {
            let captureArea = null;
            const sel = transformer.nodes()[0];
            const btn = document.querySelector('button[onclick*="extractTextFromScreen"]');

            if (sel) {
                // Coordenadas de TELA para o nó selecionado
                const pos = sel.getAbsolutePosition();
                const scale = stage.scaleX();
                captureArea = {
                    x: pos.x - (10 * scale),
                    y: pos.y - (10 * scale),
                    width: (sel.width() * sel.scaleX() * scale) + (20 * scale),
                    height: (sel.height() * sel.scaleY() * scale) + (20 * scale)
                };
            } else if (lastSelectionBox && lastSelectionBox.screen) {
                captureArea = lastSelectionBox.screen;
            }

            if (!captureArea) {
                alert("Selecione um texto ou desenhe uma área no canvas.");
                return;
            }

            if (btn) { btn.innerText = "⏳ Lendo..."; btn.disabled = true; }

            const oldNodes = transformer.nodes();
            transformer.nodes([]);
            layer.draw();

            try {
                // --- OCR PRECISION v27.9: Captura do STAGE (Global) ---
                const dataUrl = stage.toDataURL({
                    x: captureArea.x,
                    y: captureArea.y,
                    width: captureArea.width,
                    height: captureArea.height,
                    pixelRatio: 2.0 // Viewport capture não precisa de 4x (v27.9 balanceado)
                });

                const blob = await (await fetch(dataUrl)).blob();
                const formData = new FormData();
                formData.append('image', blob, 'capture.png');

                const res = await fetch('/extract', { method: 'POST', body: formData });
                const data = await res.json();

                if (data.text) {
                    const content = document.getElementById('sidebar-text-content');
                    if (content) {
                        content.value = data.text;
                        editor.updateSelectedText();
                    }
                } else if (data.error) {
                    alert("Erro OCR: " + data.error);
                } else {
                    console.log("OCR Tesseract: Nenhum texto detectado.");
                }
            } catch (e) {
                console.error("Falha OCR:", e);
                alert("Erro ao comunicar com o motor Tesseract.");
            } finally {
                transformer.nodes(oldNodes);
                layer.draw();
                if (btn) { btn.innerText = "🔍 Extrair OCR"; btn.disabled = false; }
            }
        }
    };
})();

window.editor = editor;
window.addText = () => editor.addText();
window.updateSelectedText = () => editor.updateSelectedText();
window.exportImage = () => editor.exportImage();
window.triggerUpload = () => {
    const input = document.getElementById('image-upload');
    if (input) input.click();
};

function updateSidebar(node) {
    const content = document.getElementById('sidebar-text-content');
    if (!content) return;
    if (node.hasOwnProperty('text') || node.getClassName() === 'Text') {
        const isText = node.getClassName() === 'Text';
        const attrs = node.getAttrs();

        content.value = isText ? node.text() : (node.getAttr('sfxText') || "");

        if (isText) {
            document.getElementById('font-size').value = attrs.fontSize || 40;
            document.getElementById('font-family').value = attrs.fontFamily || 'Arial';
            document.getElementById('font-weight').value = attrs.fontStyle || 'normal';
            document.getElementById('text-color').value = attrs.fill || '#000000';
            document.getElementById('stroke-width').value = attrs.strokeWidth || 0;
            document.getElementById('stroke-color').value = attrs.stroke || '#ffffff';

            // Novos Atributos v28.5
            document.getElementById('letter-spacing').value = attrs.letterSpacing || 0;
            document.getElementById('line-height').value = attrs.lineHeight || 1;
            document.getElementById('scale-x').value = attrs.scaleX || 1;
            document.getElementById('skew-x').value = attrs.skewX || 0;
            document.getElementById('skew-y').value = attrs.skewY || 0;

            // Sombra
            const shadowOn = attrs.shadowEnabled || false;
            document.getElementById('text-shadow').checked = shadowOn;
            document.getElementById('shadow-blur').value = attrs.shadowBlur || 5;
            document.getElementById('shadow-offset').value = attrs.shadowOffset ? attrs.shadowOffset.x : 2;
            document.getElementById('shadow-color').value = attrs.shadowColor || '#000000';
        }

        editor.updateHexLabels();
        if (window.styleExtract && window.styleExtract.updateLabels) {
            window.styleExtract.updateLabels();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    editor.init('container');
    if (window.navigation) window.navigation.init();
    if (window.minimap) window.minimap.init();

    const uploadInput = document.getElementById('image-upload');
    if (uploadInput) {
        uploadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (ev) => editor.loadImage(ev.target.result);
                reader.readAsDataURL(file);
            }
        });
    }

    if (window.styleExtract && window.styleExtract.init) {
        window.styleExtract.init();
    }
});
