/**
 * Módulo Social DNA Library v2 — Tipografia Dinâmica e Flexibilidade
 * FASE 7 — INTEGRAÇÃO DE FONTES E AJUSTES MALEÁVEIS
 */

window.styleExtract = (function () {
    let presets = [];

    async function init() {
        await loadFonts(); // ESSENCIAL: Carregar fontes antes dos presets
        await loadPresets();
    }

    async function loadPresets() {
        try {
            const res = await fetch('/api/list_presets');
            presets = await res.json();
            renderGallery();
        } catch (e) { console.error("Erro ao carregar presets:", e); }
    }

    async function loadFonts() {
        const select = document.getElementById('font-family');
        if (!select) return;

        try {
            console.log("%c DNA: Carregando Fontes Sênior... ", "background: #3498db; color: white");
            const res = await fetch('/api/list_fonts');
            const data = await res.json();

            select.innerHTML = '';
            const styleTag = document.createElement('style');
            styleTag.id = 'dynamic-fonts';
            document.head.appendChild(styleTag);

            let fontFaces = "";

            for (const [category, fonts] of Object.entries(data.categories)) {
                const group = document.createElement('optgroup');
                group.label = category.toUpperCase();

                fonts.forEach(f => {
                    const option = document.createElement('option');
                    // Remove extensão para o nome da família
                    const familyName = f.name.replace(/\.[^/.]+$/, "");
                    option.value = familyName;
                    option.innerText = familyName;
                    // MODO PREVIEW v28.4: Aplicar a própria fonte na opção
                    option.style.fontFamily = `'${familyName}'`;
                    option.style.fontSize = "16px"; // Tamanho confortável para preview
                    group.appendChild(option);

                    // Gerar CSS @font-face
                    const fontUrl = `/fonts/${f.path}`;
                    fontFaces += `
                        @font-face {
                            font-family: '${familyName}';
                            src: url('${fontUrl}');
                            font-display: swap;
                        }
                    `;
                });
                select.appendChild(group);
            }
            styleTag.innerHTML = fontFaces;
            console.log("DNA: Fontes carregadas com sucesso.");
        } catch (e) {
            console.error("ERRO AO CARREGAR FONTES:", e);
        }
    }

    function renderGallery() {
        const container = document.getElementById('presets-container');
        if (!container) return;
        container.innerHTML = '';

        presets.forEach(p => {
            const card = document.createElement('div');
            card.className = 'preset-card';
            card.title = "Clique para aplicar; Ajuste livremente depois!";

            // Preview de cores
            const dots = document.createElement('div');
            dots.className = 'preview-dots';

            const fillColors = p.fill.colors || ['#000000'];
            fillColors.forEach(c => {
                const dot = document.createElement('div');
                dot.className = 'dot';
                dot.style.backgroundColor = c;
                dots.appendChild(dot);
            });

            // Estilo do Texto no Card (Preview Real)
            const textStyle = `
                font-family: '${p.font_family || 'inherit'}';
                color: ${fillColors[0]};
                ${p.stroke && p.stroke.enabled ? `-webkit-text-stroke: 0.5px ${p.stroke.color};` : ''}
                ${p.shadow && p.shadow.enabled ? `text-shadow: 1px 1px 2px ${p.shadow.color};` : ''}
                font-weight: ${p.weight === 'heavy' ? '900' : (p.weight === 'bold' ? 'bold' : 'normal')};
            `;

            const author = p.author || 'Membro';
            card.innerHTML = `
                <span style="${textStyle}; font-size: 0.85rem; margin-bottom: 2px; transition: var(--transition);">${p.name}</span>
                <small style="font-size: 0.55rem; color: var(--text-dim);">por ${author}</small>
            `;
            card.prepend(dots);

            card.onclick = (e) => {
                // Efeito visual de clique "maleável"
                card.style.transform = "scale(0.95)";
                setTimeout(() => card.style.transform = "", 100);
                apply(p);
            };
            container.appendChild(card);
        });
    }

    function apply(s) {
        window.activeStyle = s;

        // 1. FONT
        if (s.font_family) {
            setValue('font-family', s.font_family);
        }

        // 2. FILL
        const fillData = s.fill || { type: 'solid', colors: ['#000000'] };
        setValue('text-color', fillData.colors[0]);
        setCheck('grad-enabled', fillData.type === 'gradient');

        if (fillData.type === 'gradient') {
            setValue('grad-color-1', fillData.colors[0]);
            setValue('grad-color-2', fillData.colors[1] || fillData.colors[0]);
            setValue('grad-direction', fillData.direction || 'vertical');
        }

        // 3. STROKE
        const strokeData = s.stroke || { enabled: false, width: 0, color: '#ffffff' };
        setValue('stroke-width', strokeData.enabled ? strokeData.width : 0);
        setValue('stroke-color', strokeData.color || '#ffffff');

        // 4. SHADOW
        const shadowData = s.shadow || { enabled: false };
        setCheck('text-shadow', shadowData.enabled);

        // 5. WEIGHT & SPACING
        const weightMap = { "light": "300", "regular": "normal", "bold": "bold", "heavy": "900" };
        const rawWeight = s.weight || 'normal';
        setValue('font-weight', weightMap[rawWeight] || rawWeight);
        setValue('letter-spacing', Math.round(s.letter_spacing) || 0);

        if (window.editor && window.editor.updateHexLabels) {
            window.editor.updateHexLabels();
            window.editor.updateSelectedText();
        }

        // MODO LIVE v28.8: Se for um SFX ou Texto, aplicar mudanças instantaneamente
        handleSliderChange();
    }

    async function saveCurrentAsPreset() {
        const name = prompt("Dê um nome ao seu estilo:");
        if (!name) return;

        const author = prompt("Seu nome de autor:") || "Membro";

        const currentStyle = {
            name: name,
            author: author,
            font_family: document.getElementById('font-family').value,
            fill: {
                type: document.getElementById('grad-enabled').checked ? 'gradient' : 'solid',
                colors: [
                    document.getElementById('text-color').value,
                    document.getElementById('grad-color-2').value
                ],
                direction: document.getElementById('grad-direction').value
            },
            stroke: {
                enabled: parseInt(document.getElementById('stroke-width').value) > 0,
                width: parseInt(document.getElementById('stroke-width').value),
                color: document.getElementById('stroke-color').value
            },
            shadow: {
                enabled: document.getElementById('text-shadow').checked,
                offset_x: 4, offset_y: 4, blur: 4, color: "#000000"
            },
            weight: document.getElementById('font-weight').value,
            letter_spacing: parseFloat(document.getElementById('letter-spacing').value)
        };

        try {
            const res = await fetch('/api/save_preset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentStyle)
            });
            const data = await res.json();
            if (data.success) {
                console.log("%c DNA: Estilo salvo com fonte incluída! ", "background: #28a745; color: white");
                await loadPresets();
            }
        } catch (e) { console.error("Erro ao salvar preset:", e); }
    }

    function setValue(id, val) { const el = document.getElementById(id); if (el) el.value = val; }
    function setCheck(id, val) { const el = document.getElementById(id); if (el) el.checked = val; }

    function updateLabels() {
        const ids = ['warp-intensity', 'sfx-arch', 'skew-x', 'skew-y', 'font-size', 'stroke-width', 'letter-spacing', 'line-height', 'scale-x', 'shadow-blur', 'shadow-offset'];
        ids.forEach(id => {
            const el = document.getElementById(id);
            const label = document.getElementById(`val-${id}`);
            if (el && label) label.innerText = el.value;
        });
    }

    async function handleSliderChange() {
        // Garantir que o valor visual do tamanho seja atualizado no label (se houver)
        updateLabels();

        // MODO LIVE v28.5: Atualizar texto normal instantaneamente
        if (window.editor && window.editor.updateSelectedText) {
            window.editor.updateSelectedText();
        }

        // Se houver um SFX renderizado selecionado, re-renderizar automaticamente (Live-ish)
        if (window.transformer) {
            const sel = window.transformer.nodes()[0];
            const isSFX = sel && (sel.hasName('rendered-sfx') || sel.getAttr('sfxText') !== undefined);
            if (isSFX) {
                const img = await renderSFX(true); // Modo silencioso
                if (img) {
                    sel.image(img);
                    sel.setAttr('styleDNA', getStyleDNA());
                    window.layer.batchDraw();
                }
            }
        }
    }

    function getStyleDNA() {
        return {
            text: document.getElementById('sidebar-text-content').value,
            fill: document.getElementById('text-color').value,
            stroke: document.getElementById('stroke-color').value,
            stroke_width: document.getElementById('stroke-width').value,
            warp_intensity: document.getElementById('warp-intensity') ? document.getElementById('warp-intensity').value : 1.0,
            arch: document.getElementById('sfx-arch') ? document.getElementById('sfx-arch').value * 1.0 : 0.0,
            font_family: document.getElementById('font-family').value || 'Arial',
            font_weight: document.getElementById('font-weight').value || 'normal',
            font_size: document.getElementById('font-size').value || 40,
            letter_spacing: document.getElementById('letter-spacing').value * 1.0 || 0,
            line_height: document.getElementById('line-height').value * 1.0 || 1.0,
            grad_enabled: document.getElementById('grad-enabled').checked,
            grad_color_1: document.getElementById('grad-color-1').value,
            grad_color_2: document.getElementById('grad-color-2').value,
            grad_direction: document.getElementById('grad-direction').value,
            scale_x: document.getElementById('scale-x') ? document.getElementById('scale-x').value * 1.0 : 1.0,
            skew_x: document.getElementById('skew-x') ? document.getElementById('skew-x').value * 1.0 : 0,
            skew_y: document.getElementById('skew-y') ? document.getElementById('skew-y').value * 1.0 : 0,
            // Sombra para o backend SFX (v28.6)
            shadow_enabled: document.getElementById('text-shadow').checked,
            shadow_blur: parseInt(document.getElementById('shadow-blur').value),
            shadow_offset: parseInt(document.getElementById('shadow-offset').value),
            shadow_color: document.getElementById('shadow-color').value
        };
    }

    async function renderSFX(silent = false) {
        let textValue = document.getElementById('sidebar-text-content').value.trim();
        // MODO RESGATE v28.8: Se estiver vazio e NÃO for modo silencioso (clique manual), usa default.
        // Se for silencioso (digitação), permitimos vazio temporário para não quebrar o fluxo.
        if (!textValue || textValue === "Selecione um texto para editar...") {
            if (!silent) {
                textValue = "SFX";
                document.getElementById('sidebar-text-content').value = "SFX";
            } else {
                textValue = " "; // Espaço em branco para renderização vazia segura
            }
        }

        const fill = document.getElementById('text-color').value;
        const stroke = document.getElementById('stroke-color').value;
        const sWidth = document.getElementById('stroke-width').value;
        const warpIntensity = document.getElementById('warp-intensity') ? document.getElementById('warp-intensity').value : 1.0;
        const sfxArch = document.getElementById('sfx-arch') ? document.getElementById('sfx-arch').value * 1.0 : 0.0;
        const fontFamily = document.getElementById('font-family').value || 'Arial';
        const fontWeight = document.getElementById('font-weight').value || 'normal';
        const fontSize = document.getElementById('font-size').value * 1.0 || 120;
        const letterSpacing = document.getElementById('letter-spacing').value * 1.0 || 0;
        const lineHeight = document.getElementById('line-height').value * 1.0 || 1.0;

        // Dados de sombra (v28.6)
        const shadowEnabled = document.getElementById('text-shadow').checked;
        const shadowBlur = document.getElementById('shadow-blur').value;
        const shadowOffset = document.getElementById('shadow-offset').value;
        const shadowColor = document.getElementById('shadow-color').value;

        // Dados de degradê (v28.7 Correction)
        const gradEnabled = document.getElementById('grad-enabled').checked;
        const gradColor1 = document.getElementById('grad-color-1').value;
        const gradColor2 = document.getElementById('grad-color-2').value;
        const gradDirection = document.getElementById('grad-direction').value;

        try {
            if (!silent) console.log("%c SFX: Renderizando Onomatopeia Dinâmica v28.6... ", "background: #e67e22; color: white");
            const res = await fetch('/api/render_sfx', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: textValue, fill, stroke, stroke_width: sWidth,
                    warp_intensity: warpIntensity, arch: sfxArch, font_family: fontFamily,
                    font_size: fontSize,
                    grad_enabled: gradEnabled,
                    grad_color_1: gradColor1,
                    grad_color_2: gradColor2,
                    grad_direction: gradDirection,
                    font_weight: fontWeight,
                    letter_spacing: letterSpacing,
                    line_height: lineHeight,
                    // Sombra v28.6
                    shadow_enabled: shadowEnabled,
                    shadow_blur: shadowBlur,
                    shadow_offset: shadowOffset,
                    shadow_color: shadowColor
                })
            });
            const data = await res.json();
            if (data.image) {
                const img = new Image();
                return new Promise((resolve) => {
                    img.onload = () => {
                        if (silent) {
                            resolve(img);
                        } else {
                            const kImg = new Konva.Image({
                                image: img,
                                x: (window.stage.width() / 2 - window.stage.x()) / window.stage.scaleX(),
                                y: (window.stage.height() / 2 - window.stage.y()) / window.stage.scaleY(),
                                draggable: true,
                                name: 'rendered-sfx'
                            });
                            kImg.setAttr('sfxText', textValue);
                            kImg.setAttr('styleDNA', getStyleDNA());
                            window.layer.add(kImg);
                            window.transformer.nodes([kImg]);
                            window.layer.draw();
                            resolve(img);
                        }
                    };
                    img.src = data.image;
                });
            }
        } catch (e) { console.error("FALHA RENDER SFX:", e); }
        return null;
    }

    return { init, renderSFX, apply, saveCurrentAsPreset, handleSliderChange, updateLabels };
})();
