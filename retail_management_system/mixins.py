from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class PaginationMixin:
    """
    Mixin to add pagination functionality to ListViews.
    Provides enhanced pagination context and handling.
    """
    paginate_by = 10  # Default pagination size

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset if needed.
        """
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return (paginator, page_obj, page_obj.object_list, page_obj.has_other_pages())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'paginator') and self.paginator:
            context.update({
                'paginator': self.paginator,
                'page_obj': self.page_obj,
                'is_paginated': self.page_obj.has_other_pages(),
                'object_list': self.page_obj.object_list,
            })
        return context
