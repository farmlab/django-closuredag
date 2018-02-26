



class EdgeAdminMixin(object):
    exclude=["entry_edge_id","direct_edge_id", "exit_edge_id","hops", "etype" ]

    def get_queryset(self, request):
        qs = super(EdgeAdminMixin, self).get_queryset(request)
        return qs.filter(etype="direct")


class VertexAdminMixin(object):
    pass
    # def get_queryset(self, request):
        # qs = super(VertexAdminMixin, self).get_queryset(request)
        # return qs.prefetch_related("children", "parents")
