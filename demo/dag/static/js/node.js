

function make_graph(G, idDiv)
{
    var g = new dagreD3.graphlib.Graph().setGraph({rankdir:"LR"});
    unselectedN = "fill:#ddd; stroke:#ddd"
    //nodes
    G.nodes.forEach( function(n){
        href = "<a href="+n.href+">"+n.name+"</a>"
        opt = {
            labelType:'html',
            label: n.selected != true ? n.name : href,
            href:n.href,
            rx:5,
            ry:5,
            class: n.type == "nodeone" ? "n1" : "repro"  ,
            style: n.selected != true ? unselectedN : "" 
        }
        g.setNode(n.id, opt)
    });

    
    directE ="stroke: #000; stroke-width: 2px;"
    generatedE = "stroke: #bbb; stroke-width: 1px; stroke-dasharray: 5, 5;"

    G.edges.forEach( function(e){
        opt = {
            //label:e.id,
            curve: d3.curveBasis,
            style: e.etype == "direct" ? directE : generatedE  ,
            //labelStyle: "font-style: italic; font-size: 11px;"
        }
        g.setEdge(e.parent, e.child, opt)
    });


    // Create the renderer
    var render = new dagreD3.render();

    // Set up an SVG group so that we can translate the final graph.
    var div = "svg#".concat(idDiv);
    var svg = d3.select(div);
    d3.select(div.concat(" g")).remove();
    var inner = svg.append("g");

    // zoom
    zoom = d3.zoom().on("zoom", function() {
      inner.attr("transform", d3.event.transform);
    });
    svg.call(zoom);
    // Run the renderer. This is what draws the final graph.
    render(inner, g);
    // Center the graph
    //var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
    //inner.attr("transform", "translate(" + xCenterOffset + ", 20)");
    //svg.attr("height", g.graph().height + 40);
}
