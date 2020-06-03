from django.views.generic.base import TemplateView, TemplateResponseMixin
from block_render import render_template_block
from django.template.response import TemplateResponse


class BlockAwareTemplateResponse(TemplateResponse):
    '''
    A subclass of TemplateResponse to easily plug block rendering into class based views.
    This implementation checks for a block name in argument called ``__part__``.
    This should simplify rendering parts of a webpage via AJAX. 
    
    For instance you could use jQuery to load a block named ``content`` into a div with ``id="contentcontainer"``::

        <script>
            $(".menulink").on('click', function (e) {
                e.preventDefault();
                var $this = $(this);
                var href = $this.attr('href');
                var $container = $("#contentcontainer");
                $.get(href, { '__part__' : 'content' }, function(resp) { $container.html(resp); });
            });
        </script>

    For a different behavior (e.g. relying on a specific HTTP header like in PJAX) you could override
    the ``get_block_part`` in your subclass.
    '''

    def get_block_part(self, request):
        if request.is_ajax():
            return request.REQUEST.get('__part__', None)

    @property
    def rendered_content(self):
        if self.block_part is not None:
            template = self.resolve_template(self.template_name)
            context = self.resolve_context(self.context_data)
            return render_template_block(template, self.block_part, context)
        else:
            return super(BlockAwareTemplateResponse, self).rendered_content

    def __init__(self, request, *args, **kwargs):
        self.block_part = self.get_block_part(request)
        return super(BlockAwareTemplateResponse, self).__init__(request, *args, **kwargs)

class BlockAwareTemplateResponseMixin(TemplateResponseMixin):
    '''
    A mixin to enable partial (block) rendering in class based views

    You can use it like this::

        class MyView(BlockAwareTemplateResponseMixin, TemplateView):
            pass
    '''
    response_class = BlockAwareTemplateResponse


