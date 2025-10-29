from plotly import exceptions, optional_imports
from plotly.graph_objs import graph_objs

pd = optional_imports.get_module("pandas")


def validate_table(table_text, font_colors):
    """
    Table-specific validations

    Check that font_colors is supplied correctly (1, 3, or len(text)
        colors).

    :raises: (PlotlyError) If font_colors is supplied incorretly.

    See FigureFactory.create_table() for params
    """
    # Inline calculation as tuple for faster lookups
    font_colors_len_options = (1, 3, len(table_text))
    if len(font_colors) not in font_colors_len_options:
        raise exceptions.PlotlyError(
            "Oops, font_colors should be a list of length 1, 3 or len(text)"
        )


def create_table(
    table_text,
    colorscale=None,
    font_colors=None,
    index=False,
    index_title="",
    annotation_offset=0.45,
    height_constant=30,
    hoverinfo="none",
    **kwargs,
):
    """
    Function that creates data tables.

    See also the plotly.graph_objects trace
    :class:`plotly.graph_objects.Table`

    :param (pandas.Dataframe | list[list]) text: data for table.
    :param (str|list[list]) colorscale: Colorscale for table where the
        color at value 0 is the header color, .5 is the first table color
        and 1 is the second table color. (Set .5 and 1 to avoid the striped
        table effect). Default=[[0, '#66b2ff'], [.5, '#d9d9d9'],
        [1, '#ffffff']]
    :param (list) font_colors: Color for fonts in table. Can be a single
        color, three colors, or a color for each row in the table.
        Default=['#000000'] (black text for the entire table)
    :param (int) height_constant: Constant multiplied by # of rows to
        create table height. Default=30.
    :param (bool) index: Create (header-colored) index column index from
        Pandas dataframe or list[0] for each list in text. Default=False.
    :param (string) index_title: Title for index column. Default=''.
    :param kwargs: kwargs passed through plotly.graph_objs.Heatmap.
        These kwargs describe other attributes about the annotated Heatmap
        trace such as the colorscale. For more information on valid kwargs
        call help(plotly.graph_objs.Heatmap)

    Example 1: Simple Plotly Table

    >>> from plotly.figure_factory import create_table

    >>> text = [['Country', 'Year', 'Population'],
    ...         ['US', 2000, 282200000],
    ...         ['Canada', 2000, 27790000],
    ...         ['US', 2010, 309000000],
    ...         ['Canada', 2010, 34000000]]

    >>> table = create_table(text)
    >>> table.show()

    Example 2: Table with Custom Coloring

    >>> from plotly.figure_factory import create_table
    >>> text = [['Country', 'Year', 'Population'],
    ...         ['US', 2000, 282200000],
    ...         ['Canada', 2000, 27790000],
    ...         ['US', 2010, 309000000],
    ...         ['Canada', 2010, 34000000]]
    >>> table = create_table(text,
    ...                      colorscale=[[0, '#000000'],
    ...                                  [.5, '#80beff'],
    ...                                  [1, '#cce5ff']],
    ...                      font_colors=['#ffffff', '#000000',
    ...                                 '#000000'])
    >>> table.show()

    Example 3: Simple Plotly Table with Pandas

    >>> from plotly.figure_factory import create_table
    >>> import pandas as pd
    >>> df = pd.read_csv('http://www.stat.ubc.ca/~jenny/notOcto/STAT545A/examples/gapminder/data/gapminderDataFiveYear.txt', sep='	')
    >>> df_p = df[0:25]
    >>> table_simple = create_table(df_p)
    >>> table_simple.show()

    """

    # Avoiding mutables in the call signature
    colorscale = (
        colorscale
        if colorscale is not None
        else [[0, "#00083e"], [0.5, "#ededee"], [1, "#ffffff"]]
    )
    font_colors = (
        font_colors if font_colors is not None else ["#ffffff", "#000000", "#000000"]
    )

    validate_table(table_text, font_colors)
    # Only create one _Table object for both matrix and annotations
    tbl = _Table(
        table_text,
        colorscale,
        font_colors,
        index,
        index_title,
        annotation_offset,
        **kwargs,
    )
    table_matrix = tbl.get_table_matrix()
    annotations = tbl.make_table_annotations()

    trace = dict(
        type="heatmap",
        z=table_matrix,
        opacity=0.75,
        colorscale=colorscale,
        showscale=False,
        hoverinfo=hoverinfo,
        **kwargs,
    )

    data = [trace]
    layout = dict(
        annotations=annotations,
        height=len(table_matrix) * height_constant + 50,
        margin=dict(t=0, b=0, r=0, l=0),
        yaxis=dict(
            autorange="reversed",
            zeroline=False,
            gridwidth=2,
            ticks="",
            dtick=1,
            tick0=0.5,
            showticklabels=False,
        ),
        xaxis=dict(
            zeroline=False,
            gridwidth=2,
            ticks="",
            dtick=1,
            tick0=-0.5,
            showticklabels=False,
        ),
    )
    return graph_objs.Figure(data=data, layout=layout)


class _Table(object):
    """
    Refer to TraceFactory.create_table() for docstring
    """

    def __init__(
        self,
        table_text,
        colorscale,
        font_colors,
        index,
        index_title,
        annotation_offset,
        **kwargs,
    ):
        # Optimize DataFrame conversion by materializing only once
        if pd and isinstance(table_text, pd.DataFrame):
            headers = table_text.columns.tolist()
            table_text_index = table_text.index.tolist()
            # .values.tolist() is fastest for conversion
            table_text = table_text.values.tolist()
            table_text.insert(0, headers)
            if index:
                table_text_index.insert(0, index_title)
                # Use zip here to avoid indexing multiple times
                for arr, idx in zip(table_text, table_text_index):
                    arr.insert(0, idx)
        self.table_text = table_text
        self.colorscale = colorscale
        self.font_colors = font_colors
        self.index = index
        self.annotation_offset = annotation_offset
        # Precompute x, y as lists for slightly faster access/indexing
        # since range objects are slower for repeated indexing than lists
        self.x = list(range(len(table_text[0])))
        self.y = list(range(len(table_text)))

    def get_table_matrix(self):
        """
        Create z matrix to make heatmap with striped table coloring

        :rtype (list[list]) table_matrix: z matrix to make heatmap with striped
            table coloring.
        """
        nrows = len(self.table_text)
        ncols = len(self.table_text[0])

        # Avoid repeated len() calls and for efficiency, preallocate with direct references
        # To avoid mutating the template rows (since they are assigned directly),
        # we clone them for each assignment, which is required since later we overwrite cells of some rows
        header = [0] * ncols
        odd_row = [0.5] * ncols
        even_row = [1] * ncols

        table_matrix = [None] * nrows
        table_matrix[0] = header[:]
        # Optimize row assignment loops to a single pass, with slice assignment
        for i in range(1, nrows):
            if i % 2 == 1:
                table_matrix[i] = odd_row[:]
            else:
                table_matrix[i] = even_row[:]

        if self.index:
            # Optimize index coloring by direct indexing, avoids overhead of Python iterator
            for i in range(nrows):
                table_matrix[i][0] = 0

        return table_matrix

    def get_table_font_color(self):
        """
        Fill font-color array.

        Table text color can vary by row so this extends a single color or
        creates an array to set a header color and two alternating colors to
        create the striped table pattern.

        :rtype (list[list]) all_font_colors: list of font colors for each row
            in table.
        """
        if len(self.font_colors) == 1:
            all_font_colors = self.font_colors * len(self.table_text)
        elif len(self.font_colors) == 3:
            all_font_colors = list(range(len(self.table_text)))
            all_font_colors[0] = self.font_colors[0]
            for i in range(1, len(self.table_text), 2):
                all_font_colors[i] = self.font_colors[1]
            for i in range(2, len(self.table_text), 2):
                all_font_colors[i] = self.font_colors[2]
        elif len(self.font_colors) == len(self.table_text):
            all_font_colors = self.font_colors
        else:
            all_font_colors = ["#000000"] * len(self.table_text)
        return all_font_colors

    def make_table_annotations(self):
        """
        Generate annotations to fill in table text

        :rtype (list) annotations: list of annotations for each cell of the
            table.
        """
        all_font_colors = _Table.get_table_font_color(self)
        annotations = []
        # Pre-bind methods and attribute lookups for small attribute access win
        table_text = self.table_text
        font_colors_0 = self.font_colors[0]
        annotation_offset = self.annotation_offset
        x = self.x
        y = self.y
        index = self.index

        # Pre-Bind graph_objs.layout.Annotation to local
        Annotation = graph_objs.layout.Annotation

        # Slight speedup by removing second level variable lookup in loops
        append_ann = annotations.append

        # Instead of enumerate, use while loop for tight inner loop
        nrows = len(table_text)
        for n in range(nrows):
            row = table_text[n]
            all_font_color = all_font_colors[n]
            mcols = len(row)
            for m in range(mcols):
                val = row[m]
                # Bold text in header and index
                if n == 0 or (index and m < 1):
                    format_text = "<b>" + str(val) + "</b>"
                else:
                    format_text = str(val)
                # Match font color of index to font color of header
                if index and m == 0:
                    font_color = font_colors_0
                else:
                    font_color = all_font_color
                # Don't factor out keyword arguments for Attribute creation, preserve logic and signature
                append_ann(
                    Annotation(
                        text=format_text,
                        x=x[m] - annotation_offset,
                        y=y[n],
                        xref="x1",
                        yref="y1",
                        align="left",
                        xanchor="left",
                        font=dict(color=font_color),
                        showarrow=False,
                    )
                )
        return annotations
