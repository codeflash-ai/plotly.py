# some functions defined here to avoid numpy import


def _mean(x):
    n = len(x)
    if n == 0:
        raise ValueError("x must have positive length")
    return float(sum(x)) / n


def _argmin(x):
    min_index = 0
    min_value = x[0]
    for i in range(1, len(x)):
        if x[i] < min_value:
            min_index = i
            min_value = x[i]
    return min_index


def _argmax(x):
    max_index = 0
    max_value = x[0]
    for i in range(1, len(x)):
        if x[i] > max_value:
            max_index = i
            max_value = x[i]
    return max_index


def _df_anno(xanchor, yanchor, x, y):
    """Default annotation parameters"""
    return dict(xanchor=xanchor, yanchor=yanchor, x=x, y=y, showarrow=False)


def _add_inside_to_position(pos):
    if not ("inside" in pos or "outside" in pos):
        pos.add("inside")
    return pos


def _prepare_position(position, prepend_inside=False):
    if position is None:
        position = "top right"
    pos_str = position
    position = set(position.split(" "))
    if prepend_inside:
        position = _add_inside_to_position(position)
    return position, pos_str


def annotation_params_for_line(shape_type, shape_args, position):
    # all x0, x1, y0, y1 are used to place the annotation, that way it could
    # work with a slanted line
    # even with a slanted line, there are the horizontal and vertical
    # conventions of placing a shape
    x0 = shape_args["x0"]
    x1 = shape_args["x1"]
    y0 = shape_args["y0"]
    y1 = shape_args["y1"]
    X = (x0, x1)
    Y = (y0, y1)
    R = "right"
    T = "top"
    L = "left"
    C = "center"
    B = "bottom"
    M = "middle"

    # Compute values with tuples to avoid unnecessary list objects
    aY = y0 if y0 > y1 else y1
    iY = y0 if y0 < y1 else y1
    # Explicit float division for mean (using _mean is slower than inline calculation for two elements)
    eY = (y0 + y1) / 2.0
    aaY = 0 if y0 > y1 else 1
    aiY = 0 if y0 < y1 else 1

    aX = x0 if x0 > x1 else x1
    iX = x0 if x0 < x1 else x1
    eX = (x0 + x1) / 2.0
    aaX = 0 if x0 > x1 else 1
    aiX = 0 if x0 < x1 else 1

    position, pos_str = _prepare_position(position)
    if shape_type == "vline":
        if position == {"top", "left"}:
            return _df_anno(R, T, X[aaY], aY)
        if position == {"top", "right"}:
            return _df_anno(L, T, X[aaY], aY)
        if position == {"top"}:
            return _df_anno(C, B, X[aaY], aY)
        if position == {"bottom", "left"}:
            return _df_anno(R, B, X[aiY], iY)
        if position == {"bottom", "right"}:
            return _df_anno(L, B, X[aiY], iY)
        if position == {"bottom"}:
            return _df_anno(C, T, X[aiY], iY)
        if position == {"left"}:
            return _df_anno(R, M, eX, eY)
        if position == {"right"}:
            return _df_anno(L, M, eX, eY)
    elif shape_type == "hline":
        if position == {"top", "left"}:
            return _df_anno(L, B, iX, Y[aiX])
        if position == {"top", "right"}:
            return _df_anno(R, B, aX, Y[aaX])
        if position == {"top"}:
            return _df_anno(C, B, eX, eY)
        if position == {"bottom", "left"}:
            return _df_anno(L, T, iX, Y[aiX])
        if position == {"bottom", "right"}:
            return _df_anno(R, T, aX, Y[aaX])
        if position == {"bottom"}:
            return _df_anno(C, T, eX, eY)
        if position == {"left"}:
            return _df_anno(R, M, iX, Y[aiX])
        if position == {"right"}:
            return _df_anno(L, M, aX, Y[aaX])
    raise ValueError('Invalid annotation position "%s"' % (pos_str,))


def annotation_params_for_rect(shape_type, shape_args, position):
    x0 = shape_args["x0"]
    x1 = shape_args["x1"]
    y0 = shape_args["y0"]
    y1 = shape_args["y1"]

    position, pos_str = _prepare_position(position, prepend_inside=True)
    # Precompute common values for re-use
    minx = x0 if x0 < x1 else x1
    maxx = x0 if x0 > x1 else x1
    miny = y0 if y0 < y1 else y1
    maxy = y0 if y0 > y1 else y1
    meanx = (x0 + x1) / 2.0
    meany = (y0 + y1) / 2.0

    if position == {"inside", "top", "left"}:
        return _df_anno("left", "top", minx, maxy)
    if position == {"inside", "top", "right"}:
        return _df_anno("right", "top", maxx, maxy)
    if position == {"inside", "top"}:
        return _df_anno("center", "top", meanx, maxy)
    if position == {"inside", "bottom", "left"}:
        return _df_anno("left", "bottom", minx, miny)
    if position == {"inside", "bottom", "right"}:
        return _df_anno("right", "bottom", maxx, miny)
    if position == {"inside", "bottom"}:
        return _df_anno("center", "bottom", meanx, miny)
    if position == {"inside", "left"}:
        return _df_anno("left", "middle", minx, meany)
    if position == {"inside", "right"}:
        return _df_anno("right", "middle", maxx, meany)
    if position == {"inside"}:
        # TODO: Do we want this?
        return _df_anno("center", "middle", meanx, meany)
    if position == {"outside", "top", "left"}:
        return _df_anno(
            "right" if shape_type == "vrect" else "left",
            "bottom" if shape_type == "hrect" else "top",
            minx,
            maxy,
        )
    if position == {"outside", "top", "right"}:
        return _df_anno(
            "left" if shape_type == "vrect" else "right",
            "bottom" if shape_type == "hrect" else "top",
            maxx,
            maxy,
        )
    if position == {"outside", "top"}:
        return _df_anno("center", "bottom", meanx, maxy)
    if position == {"outside", "bottom", "left"}:
        return _df_anno(
            "right" if shape_type == "vrect" else "left",
            "top" if shape_type == "hrect" else "bottom",
            minx,
            miny,
        )
    if position == {"outside", "bottom", "right"}:
        return _df_anno(
            "left" if shape_type == "vrect" else "right",
            "top" if shape_type == "hrect" else "bottom",
            maxx,
            miny,
        )
    if position == {"outside", "bottom"}:
        return _df_anno("center", "top", meanx, miny)
    if position == {"outside", "left"}:
        return _df_anno("right", "middle", minx, meany)
    if position == {"outside", "right"}:
        return _df_anno("left", "middle", maxx, meany)
    raise ValueError("Invalid annotation position %s" % (pos_str,))


def axis_spanning_shape_annotation(annotation, shape_type, shape_args, kwargs):
    """
    annotation: a go.layout.Annotation object, a dict describing an annotation, or None
    shape_type: one of 'vline', 'hline', 'vrect', 'hrect' and determines how the
                x, y, xanchor, and yanchor values are set.
    shape_args: the parameters used to draw the shape, which are used to place the annotation
    kwargs:     a dictionary that was the kwargs of a
                _process_multiple_axis_spanning_shapes spanning shapes call. Items in this
                dict whose keys start with 'annotation_' will be extracted and the keys with
                the 'annotation_' part stripped off will be used to assign properties of the
                new annotation.

    Property precedence:
    The annotation's x, y, xanchor, and yanchor properties are set based on the
    shape_type argument. Each property already specified in the annotation or
    through kwargs will be left as is (not replaced by the value computed using
    shape_type). Note that the xref and yref properties will in general get
    overwritten if the result of this function is passed to an add_annotation
    called with the row and col parameters specified.

    Returns an annotation populated with fields based on the
    annotation_position, annotation_ prefixed kwargs or the original annotation
    passed in to this function.
    """
    # set properties based on annotation_ prefixed kwargs
    prefix = "annotation_"
    len_prefix = len(prefix)

    # Filter annotation_keys and gather values in a single pass, more efficient than repeated filters
    annotation_keys = []
    pos_val = None
    for k in kwargs:
        if k.startswith(prefix):
            annotation_keys.append(k)
            if k == "annotation_position":
                pos_val = kwargs[k]

    if annotation is None and not annotation_keys:
        return None
    # TODO: Would it be better if annotation were initialized to an instance of
    # go.layout.Annotation ?
    if annotation is None:
        annotation = dict()
    for k in annotation_keys:
        if k == "annotation_position":
            # don't set so that Annotation constructor doesn't complain
            continue
        subk = k[len_prefix:]
        annotation[subk] = kwargs[k]
    # Use annotation_position if supplied, else None
    annotation_position = pos_val

    if shape_type.endswith("line"):
        shape_dict = annotation_params_for_line(
            shape_type, shape_args, annotation_position
        )
    elif shape_type.endswith("rect"):
        shape_dict = annotation_params_for_rect(
            shape_type, shape_args, annotation_position
        )
    # Use .items() instead of .keys() + [k] for efficiency
    for k, v in shape_dict.items():
        # only set property derived from annotation_position if it hasn't already been set
        # only set property derived from annotation_position if it hasn't already been set
        # see above: this would be better as a go.layout.Annotation then the key
        # would be checked for validity here (otherwise it is checked later,
        # which I guess is ok too)
        if (k not in annotation) or (annotation[k] is None):
            annotation[k] = v
    return annotation


def split_dict_by_key_prefix(d, prefix):
    """
    Returns two dictionaries, one containing all the items whose keys do not
    start with a prefix and another containing all the items whose keys do start
    with the prefix. Note that the prefix is not removed from the keys.
    """
    no_prefix = dict()
    with_prefix = dict()
    for k in d.keys():
        if k.startswith(prefix):
            with_prefix[k] = d[k]
        else:
            no_prefix[k] = d[k]
    return (no_prefix, with_prefix)
