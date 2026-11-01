import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patches
D = os.path.dirname(os.path.abspath(__file__))
SRC = {"FIT": D + "/orig/toafit.html",
       "AOM": D + "/orig/toaom.html"}

BASE = ("[hidden]:not([hidden=until-found i]){display:none!important}"
        "img{max-width:100%}"
        ":host{display:block}"
        ".tl-body{margin:0;min-height:calc(100vh - var(--tl-bar,52px));font:14px -apple-system,BlinkMacSystemFont,sans-serif}\n")


def scope_css(css):
    css = css.replace(':root:not([data-theme="light"])', ':host(:not([data-theme="light"]))')
    css = css.replace(':root:not([data-theme="dark"])', ':host(:not([data-theme="dark"]))')
    css = css.replace(':root[data-theme="dark"]', ':host([data-theme="dark"])')
    css = css.replace(':root[data-theme="light"]', ':host([data-theme="light"])')
    css = css.replace(':root', ':host')
    css = re.sub(r'(?<![\w.#-])html(?![\w-])', ':host', css)
    css = re.sub(r'(?<![\w.#-])body(?![\w-])', '.tl-body', css)
    css = css.replace('position:sticky;top:env(safe-area-inset-top,0px)',
                      'position:sticky;top:calc(env(safe-area-inset-top,0px) + var(--tl-bar,52px))')
    return css


def split(path):
    s = open(path, encoding="utf8").read()
    styles = re.findall(r'<style>(.*?)</style>', s, re.S)
    css = "\n".join(styles[1:])  # styles[0] is the publish skeleton reset
    scripts = re.findall(r'<script>(.*?)</script>', s, re.S)
    assert len(scripts) == 1
    js = scripts[0]
    body = s[s.index('<body>') + 6:]
    body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<style>.*?</style>', '', body, flags=re.S)
    body = re.sub(r'<title>.*?</title>', '', body, flags=re.S)
    body = re.sub(r'<(meta|link)\b[^>]*>', '', body)
    body = body.replace('</body></html>', '').strip()
    assert '</template>' not in body and '</template>' not in css
    return scope_css(css), body, js


shell = open(D + "/shell.html", encoding="utf8").read()
for k in ["FIT", "AOM"]:
    css, body, js = split(SRC[k])
    if k == "FIT":
        js = patches.patch_fit_js(js)
        body, css = patches.patch_fit_body(body, css)
        css = patches.patch_fit_layout_css(css)
        js = patches.patch_fit_layout_js(js)
        js = patches.patch_fit_photo_js(js)
        js, body, css = patches.patch_fit_burn(js, body, css)
        js = patches.patch_fit_eat_toggle(js)
        js = patches.patch_fit_totals_fix(js)
    else:
        js = patches.patch_aom_js(js)
        css = patches.patch_aom_css(css)
        css = patches.patch_aom_layout_css(css)
        body = patches.patch_aom_body(body)
    tpl = "<style>" + BASE + css + "</style><div class=\"tl-body\">" + body + "</div>"
    shell = shell.replace("{{%s_TPL}}" % k, tpl).replace("{{%s_JS}}" % k, js)
assert "{{" not in re.sub(r'\$\{\{', '', shell) or True
out = os.path.join(D, "..", "toalife.html")
open(out, "w", encoding="utf8").write(shell)
print(out, len(shell))
