class FontSystem {

    constructor() {
        this.categorySelect = document.getElementById("font-category");
        this.fontSelect = document.getElementById("font-name");
        this.fontData = {};
    }

    init() {
        // Atualiza referências caso tenham sido reinjetadas no DOM
        this.categorySelect = document.getElementById("font-category");
        this.fontSelect = document.getElementById("font-name");

        if (!this.categorySelect || !this.fontSelect) {
            console.warn("FontSystem: elementos não encontrados no DOM.");
            return;
        }

        this.loadFonts();
    }

    async loadFonts() {
        try {
            const response = await fetch("/api/fonts");

            if (!response.ok) {
                throw new Error("Falha ao buscar fontes");
            }

            this.fontData = await response.json();
            this.populateCategories();
            this.injectFontStyles();
            this.attachEvents();

        } catch (error) {
            console.error("Erro ao carregar sistema de fontes:", error);
        }
    }

    populateCategories() {
        if (!this.categorySelect) return;
        this.categorySelect.innerHTML = "";

        Object.keys(this.fontData).forEach(category => {
            const option = document.createElement("option");
            option.value = category;
            option.textContent = category;
            this.categorySelect.appendChild(option);
        });

        if (Object.keys(this.fontData).length > 0) {
            this.populateFonts(this.categorySelect.value);
        }
    }

    populateFonts(category) {
        if (!this.fontSelect) return;
        this.fontSelect.innerHTML = "";

        if (!this.fontData[category]) return;

        this.fontData[category].forEach(font => {
            const fontName = typeof font === 'string' ? font : font.name;
            const option = document.createElement("option");
            option.value = fontName;
            option.textContent = fontName;
            this.fontSelect.appendChild(option);
        });

        this.fontSelect.dispatchEvent(new Event('change'));
    }

    attachEvents() {
        if (!this.categorySelect || !this.fontSelect) return;

        // Remove listeners antigos se houver (idempotência básica)
        this.categorySelect.onchange = (e) => this.populateFonts(e.target.value);

        this.fontSelect.onchange = (e) => {
            if (typeof updateSelectedTextFont === 'function') {
                updateSelectedTextFont();
            }
        };
    }

    injectFontStyles() {
        let style = document.getElementById('dynamic-font-styles');
        if (!style) {
            style = document.createElement('style');
            style.id = 'dynamic-font-styles';
            document.head.appendChild(style);
        }

        let css = '';
        if (this.fontData.custom) {
            this.fontData.custom.forEach(filename => {
                css += `
                    @font-face {
                        font-family: "${filename}";
                        src: url("/assets/fonts/custom/${filename}");
                    }
                `;
            });
        }
        style.innerHTML = css;
    }

    async importCustomFont() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.ttf,.otf';
        input.onchange = async () => {
            const file = input.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const resp = await fetch('/api/import-font', {
                    method: 'POST',
                    body: formData
                });

                if (resp.ok) {
                    alert('Fonte importada com sucesso!');
                    await this.loadFonts();
                } else {
                    const err = await resp.json();
                    alert('Erro ao importar fonte: ' + (err.error || 'Desconhecido'));
                }
            } catch (e) {
                alert('Erro de conexão.');
            }
        };
        input.click();
    }
}

let fontSystem;

function initFontSystem() {
    if (!fontSystem) {
        fontSystem = new FontSystem();
    }
    fontSystem.init();
}

document.addEventListener("DOMContentLoaded", initFontSystem);

// Global bridge
function importCustomFont() {
    if (fontSystem) fontSystem.importCustomFont();
}
