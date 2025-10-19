from django.views.generic import ListView
from django.http import Http404

class PaginationMixin(ListView):
    """
    Mixin to handle special page values like 'last' in pagination.
    Converts 'last' to the actual last page number.
    Raises 404 for invalid page values.
    """
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page')
        if page is not None:
            if page == 'last':
                queryset = self.get_queryset()
                paginator = self.get_paginator(queryset, self.get_paginate_by(queryset))
                if paginator.num_pages > 0:
                    page = paginator.num_pages
                else:
                    page = 1
                # Modify the querydict to set the page number
                request.GET = request.GET.copy()
                request.GET['page'] = str(page)
            else:
                try:
                    int(page)
                except ValueError:
                    raise Http404("Page not found")
        return super().get(request, *args, **kwargs)
