

#--------------------------------------------------------------------------------------------------


class SpacelessMiddleware(object):

    def process_response(self, request, response):
        if 'text/html' in response['Content-Type'] and len(response.content) != 0:
            content = response.content.split("\n")
            out = []
            for line in content:
                s = line.strip()
                if len(s) != 0:
                    out.append(s)
            response.content = "\n".join(out)

        return response


#--------------------------------------------------------------------------------------------------
