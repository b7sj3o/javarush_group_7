from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size" # ?page_size=40
    page_query_param = "page_number"
    max_page_size = 100

    def get_paginated_response(self, data):
        # return Response(data)
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'pages': self.page.paginator.num_pages,
                'current': self.page.number,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "required": ["pagination", "results"],
            "properties": {
                "pagination": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "example": 100},
                        "pages": {"type": "integer", "example": 5},
                        "current": {"type": "integer", "example": 1},
                        "next": {"type": "string", "nullable": True, "format": "uri"},
                        "previous": {"type": "string", "nullable": True, "format": "uri"},
                    }
                },
                "results": schema
            }
        }