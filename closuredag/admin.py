



class EdgeAdminMixin(object):
    def get_queryset(self, request):
        qs = super(EdgeAdminMixin, self).get_queryset(request)
        return qs.filter(etype="direct")


class VertexAdminMixin(object):
    pass
    # def get_queryset(self, request):
        # qs = super(VertexAdminMixin, self).get_queryset(request)
        # return qs.prefetch_related("children", "parents")
