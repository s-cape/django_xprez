from xprez.models import Content
from xprez import contents_manager
from django.db import models
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers.php import PhpLexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers.templates import DjangoLexer
from pygments.lexers.html import DtdLexer


class CodeSnippet(Content):
    form_class = 'xprez.code_snippet.admin_forms.CodeSnippetForm'
    admin_template_name = 'xprez/admin/code_snippet.html'
    front_template_name = 'xprez/code_snippet.html'
    verbose_name = 'Code snippet'

    class FrontMedia:
        css = ['xprez/css/pygments/colorful.css', ]

    class AdminMedia:
        js = ['xprez/js/textarea_with_tabs.js']

    LANG_CHOICES = (
        ('python', 'Python'),
        ('js', 'JavaScript'),
        ('django_template', 'Django Template'),
        ('php', 'PHP'),
        ('xml', 'XML'),
    )

    title = models.CharField(max_length=150, null=True, blank=True)
    code = models.TextField()
    lang = models.CharField('Jazyk', max_length=20, choices=LANG_CHOICES, default='python')

    def get_highlighted_code(self):
        lexer_map = {
            'js': JavascriptLexer,
            'python': PythonLexer,
            'django_template': DjangoLexer,
            'php': PhpLexer,
            'xml': DtdLexer,
        }
        return highlight(self.code, lexer_map[self.lang](), HtmlFormatter(style='colorful'))


contents_manager.register(CodeSnippet)
