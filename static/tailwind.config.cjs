module.exports = {
  content: ['./static/index.html', './app/main_ui/**/*.js'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: (() => {
        const v = (n) => `rgb(var(--${n}) / <alpha-value>)`;
        const fam = (n, sh) => Object.fromEntries(sh.map((x) => [x, v(`${n}-${x}`)]));
        const c5 = [100, 200, 300, 400, 500];
        return {
          white: v('w'),
          zinc: fam('z', [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]),
          emerald: fam('emerald', c5),
          cyan: fam('cyan', c5),
          fuchsia: fam('fuchsia', c5),
          purple: fam('purple', c5),
          rose: fam('rose', c5),
          orange: fam('orange', c5),
          amber: fam('amber', c5),
          lime: fam('lime', c5),
        };
      })(),
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
    },
  },
};
