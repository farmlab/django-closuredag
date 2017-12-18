# dict recurse template tag for django
# from http://djangosnippets.org/snippets/1974/

from django import template

register = template.Library()


class RecurseDictVertex(template.Node):
    def __init__(self, var, vertexList):
        self.var = var
        self.vertexList = vertexList

    def __repr__(self):
        return '<RecurseDictVertex>'

    def renderCallback(self, context, vals, level):
        if len(vals) == 0:
            return ''

        output = []

        if 'loop' in self.vertexList:
            output.append(self.vertexList['loop'].render(context))

        for k, v in vals:
            context.push()

            context['level'] = level
            context['key'] = k

            if 'value' in self.vertexList:
                output.append(self.vertexList['value'].render(context))

                if type(v) == list or type(v) == tuple:
                    child_items = [ (None, x) for x in v ]
                    output.append(self.renderCallback(context, child_items, level + 1))
                else:
                    try:
                        child_items = v.items()
                        output.append(self.renderCallback(context, child_items, level + 1))
                    except:
                        output.append(unicode(v))

            if 'endloop' in self.vertexList:
                output.append(self.vertexList['endloop'].render(context))
            else:
                output.append(self.vertexList['endrecursedict'].render(context))

            context.pop()

        if 'endloop' in self.vertexList:
            output.append(self.vertexList['endrecursedict'].render(context))

        return ''.join(output)

    def render(self, context):
        vals = self.var.resolve(context).items()
        output = self.renderCallback(context, vals, 1)
        return output


def recursedict_tag(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2 and bits[0] != 'recursedict':
        raise template.TemplateSyntaxError("Invalid tag syntax expected '{% recursedict [dictVar] %}'")

    var = parser.compile_filter(bits[1])
    vertexList = {}
    while len(vertexList) < 4:
        temp = parser.parse(('value','loop','endloop','endrecursedict'))
        tag = parser.tokens[0].contents
        vertexList[tag] = temp
        parser.delete_first_token()
        if tag == 'endrecursedict':
            break

    return RecurseDictVertex(var, vertexList)

recursedict_tag = register.tag('recursedict', recursedict_tag)
