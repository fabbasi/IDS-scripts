.. py:currentmodule:: Orange.feature

==========
Descriptor
==========

Data instances in Orange can contain several types of variables:
:ref:`discrete <discrete>`, :ref:`continuous <continuous>`,
:ref:`strings <string>`, and :ref:`Python <Python>` and types derived
from it.  The latter represent arbitrary Python objects.  The names,
types, values (where applicable), functions for computing the variable
value from values of other variables, and other properties of the
variables are stored in descriptor classes derived from
:obj:`Descriptor`.

Orange considers two variables (e.g. in two different data tables) the
same if they have the same descriptor. It is allowed - but not
recommended - to have different descriptors with the same name.

Descriptors can be constructed either by calling the corresponding
constructors or by a factory function :func:`make`, which either
retrieves an existing descriptor or constructs a new one.

.. class:: Descriptor

    An abstract base class for variable descriptors.

    .. attribute:: name

        The name of the variable.

    .. attribute:: var_type

        Variable type; it can be :obj:`~Orange.feature.Type.Discrete`,
        :obj:`~Orange.feature.Type.Continuous`,
        :obj:`~Orange.feature.Type.String` or :obj:`~Orange.feature.Type.Other`.

    .. attribute:: get_value_from

        A function (an instance of
        :obj:`~Orange.classification.Classifier`) that computes a
        value of the variable from values of one or more other
        variables. This is used, for instance, in discretization,
        which computes the value of a discretized variable from the
        original continuous variable.

    .. attribute:: ordered

        A flag telling whether the values of a discrete variable are
        ordered. At the moment, no built-in method treats ordinal
        variables differently than nominal ones.

    .. attribute:: random_generator

        A local random number generator used by method
        :obj:`~Descriptor.randomvalue()`.

    .. attribute:: default_meta_id

        A proposed (but not guaranteed) meta id to be used for that
        variable.  For instance, when a tab-delimited contains meta
        attributes and the existing variables are reused, they will
        have this id (instead of a new one assigned by
        :obj:`Orange.feature.Descriptor.new_meta_id()`).

    .. attribute:: attributes

        A dictionary which allows the user to store additional
        information about the variable. All values should be
        strings. See the section about :ref:`storing additional
        information <attributes>`.

    .. method:: __call__(obj)

           Convert a string, number, or other suitable object into a
           variable value.

           :param obj: An object to be converted into a variable value
           :type o: any suitable
           :rtype: :class:`Orange.data.Value`

    .. method:: randomvalue()

           Return a random value for the variable.

           :rtype: :class:`Orange.data.Value`

    .. method:: compute_value(instance)

           Compute the value of the variable given the instance by
           calling obj:`~Descriptor.get_value_from` through a
           mechanism that prevents infinite recursive calls.

           :rtype: :class:`Orange.data.Value`


Discrete variables
------------------

.. _discrete:
.. class:: Discrete

    Bases: :class:`Descriptor`

    Descriptor for discrete variables.

    .. attribute:: values

        A list with symbolic names for variables' values. Values are stored as
        indices referring to this list and modifying it instantly
        changes the (symbolic) names of values as they are printed out or
        referred to by user.

        .. note::

            The size of the list is also used to indicate the number of
            possible values for this variable. Changing the size - especially
            shrinking the list - can crash Python. Also, do not add values
            to the list by calling its append or extend method:
            use :obj:`add_value` method instead.

            It is also assumed that this attribute is always defined (but can
            be empty), so never set it to ``None``.

    .. attribute:: base_value

            Stores the base value for the variable as an index in `values`.
            This can be, for instance, a "normal" value, such as "no
            complications" as opposed to abnormal "low blood pressure". The
            base value is used by certain statistics, continuization etc.
            potentially, learning algorithms. The default is -1 which means that
            there is no base value.

    .. method:: __init__(name)

        Construct a descriptor for variable with the given name.

    .. method:: add_value(s)

            Add a value with symbolic name ``s`` to values. Always call
            this function instead of appending to ``values``.

Continuous variables
--------------------

.. _continuous:
.. class:: Continuous

    Bases: :class:`Descriptor`

    Descriptor for continuous variables.

    .. attribute:: number_of_decimals

        The number of decimals used when the value is printed out, converted to
        a string or saved to a file.

    .. attribute:: scientific_format

        If ``True``, the value is printed in scientific format whenever it
        would have more than 5 digits. In this case, :obj:`number_of_decimals` is
        ignored.

    .. attribute:: adjust_decimals

        Tells Orange to monitor the number of decimals when the value is
        converted from a string (when the values are read from a file or
        converted by, e.g. ``inst[0]="3.14"``):

        * 0: the number of decimals is not adjusted automatically;
        * 1: the number of decimals is (and has already) been adjusted;
        * 2: automatic adjustment is enabled, but no values have been
          converted yet.

        By default, adjustment of the number of decimals goes as follows:

        * If the variable was constructed when data was read from a file,
          it will be printed with the same number of decimals as the
          largest number of decimals encountered in the file. If
          scientific notation occurs in the file,
          :obj:`scientific_format` will be set to ``True`` and scientific
          format will be used for values too large or too small.

        * If the variable is created in a script, it will have,
          by default, three decimal places. This can be changed either by
          setting the value from a string (e.g. ``inst[0]="3.14"``,
          but not ``inst[0]=3.14``) or by manually setting the
          :obj:`number_of_decimals`.

    .. attribute:: start_value, end_value, step_value

        The range used for :obj:`randomvalue`.

    .. method:: __init__(name)

        Construct a descriptor for variable with the given name.


String variables
----------------

.. _String:

.. class:: String

    Bases: :class:`Descriptor`

    Descriptor for variables that contain strings. No method can use them for
    learning; some will raise error or warnings, and others will
    silently ignore them. They can be, however, used as meta-attributes; if
    instances in a dataset have unique IDs, the most efficient way to store them
    is to read them as meta-attributes. In general, never use discrete
    attributes with many (say, more than 50) values. Such attributes are
    probably not of any use for learning and should be stored as string
    attributes.

    When converting strings into values and back, empty strings are treated
    differently than usual. For other types, an empty string denotes
    undefined values, while :obj:`String` will take empty strings
    as empty strings -- except when loading or saving into file.
    Empty strings in files are interpreted as undefined; to specify an empty
    string, enclose the string in double quotes; these are removed when the
    string is loaded.

    .. method:: __init__(name)

        Construct a descriptor for variable with the given name.

Python objects as variables
---------------------------

.. _Python:
.. class:: Python

    Bases: :class:`Descriptor`

    Base class for descriptors defined in Python. It is fully functional
    and can be used as a descriptor for attributes that contain arbitrary Python
    values. Since this is an advanced topic, PythonVariables are described on a
    separate page. !!TODO!!


.. _attributes:

Storing additional attributes
-----------------------------

All variables have a field :obj:`~Descriptor.attributes`, a dictionary
that can store additional string data.

.. literalinclude:: code/attributes.py

These attributes can only be saved to a .tab file. They are listed in the
third line in <name>=<value> format, after other attribute specifications
(such as "meta" or "class"), and are separated by spaces.

.. _variable_descriptor_reuse:

Reuse of descriptors
--------------------

There are situations when variable descriptors need to be
reused. Typically, the user loads some training examples, trains a
classifier, and then loads a separate test set. For the classifier to
recognize the variables in the second data set, the descriptors, not
just the names, need to be the same.

When constructing new descriptors for data read from a file or during
unpickling, Orange checks whether an appropriate descriptor (with the same
name and, in case of discrete variables, also values) already exists and
reuses it. When new descriptors are constructed by explicitly calling
the above constructors, this always creates new descriptors and thus
new variables, although a variable with the same name may already exist.

The search for an existing variable is based on four attributes: the
variable's name, type, ordered values, and unordered values. As for the
latter two, the values can be explicitly ordered by the user, e.g. in
the second line of the tab-delimited file. For instance, sizes can be
ordered as small, medium, or big.

The search for existing variables can end with one of the following
statuses.

.. data:: Descriptor.MakeStatus.NotFound (4)

    The variable with that name and type does not exist.

.. data:: Descriptor.MakeStatus.Incompatible (3)

    There are variables with matching name and type, but their values
    are incompatible with the prescribed ordered values. For example,
    if the existing variable already has values ["a", "b"] and the new
    one wants ["b", "a"], the old variable cannot be reused. The
    existing list can, however be appended with the new values, so
    searching for ["a", "b", "c"] would succeed. Likewise a search for
    ["a"] would be successful, since the extra existing value does not
    matter. The formal rule is thus that the values are compatible iff
    ``existing_values[:len(ordered_values)] ==
    ordered_values[:len(existing_values)]``.

.. data:: Descriptor.MakeStatus.NoRecognizedValues (2)

    There is a matching variable, yet it has none of the values that
    the new variable will have (this is obviously possible only if the
    new variable has no prescribed ordered values). For instance, we
    search for a variable "sex" with values "male" and "female", while
    there is a variable of the same name with values "M" and "F" (or,
    well, "no" and "yes" :). Reuse of this variable is possible,
    though this should probably be a new variable since it obviously
    comes from a different data set. If we do decide to reuse the
    variable, the old variable will get some unneeded new values and
    the new one will inherit some from the old.

.. data:: Descriptor.MakeStatus.MissingValues (1)

    There is a matching variable with some of the values that the new
    one requires, but some values are missing. This situation is
    neither uncommon nor suspicious: in case of separate training and
    testing data sets there may be values which occur in one set but
    not in the other.

.. data:: Descriptor.MakeStatus.OK (0)

    There is a perfect match which contains all the prescribed values
    in the correct order. The existing variable may have some extra
    values, though.

Continuous variables can obviously have only two statuses,
:obj:`~Descriptor.MakeStatus.NotFound` or :obj:`~Descriptor.MakeStatus.OK`.

When loading the data using :obj:`Orange.data.Table`, Orange takes the
safest approach and, by default, reuses everything that is compatible
up to and including
:obj:`~Descriptor.MakeStatus.NoRecognizedValues`. Unintended reuse
would be obvious from the variable having too many values, which the
user can notice and fix. More on that in the page on
:doc:`Orange.data.formats`.

There are two functions for reusing the variables instead of creating
new ones.

.. function:: Descriptor.make(name, type, ordered_values, unordered_values[, create_new_on])

    Find and return an existing variable or create a new one if none
    of the existing variables matches the given name, type and values.

    The optional `create_new_on` specifies the status at which a new
    variable is created. The status must be at most
    :obj:`~Descriptor.MakeStatus.Incompatible` since incompatible (or
    non-existing) variables cannot be reused. If it is set lower, for
    instance to :obj:`~Descriptor.MakeStatus.MissingValues`, a new
    variable is created even if there exists a variable which is only
    missing the same values. If set to
    :obj:`~Descriptor.MakeStatus.OK`, the function always creates a
    new variable.

    The function returns a tuple containing a variable descriptor and
    the status of the best matching variable. So, if ``create_new_on``
    is set to :obj:`~Descriptor.MakeStatus.MissingValues`, and there
    exists a variable whose status is, say,
    :obj:`~Descriptor.MakeStatus.NoRecognizedValues`, a variable would
    be created, while the second element of the tuple would contain
    :obj:`~Descriptor.MakeStatus.NoRecognizedValues`. If, on the other
    hand, there exists a variable which is perfectly OK, its
    descriptor is returned and the returned status is
    :obj:`~Descriptor.MakeStatus.OK`. The function returns no
    indicator whether the returned variable is reused or not. This can
    be, however, read from the status code: if it is smaller than the
    specified ``create_new_on``, the variable is reused, otherwise a
    new descriptor has been constructed.

    The exception to the rule is when ``create_new_on`` is OK. In this
    case, the function does not search through the existing variables
    and cannot know the status, so the returned status in this case is
    always :obj:`~Descriptor.MakeStatus.OK`.

    :param name: Descriptor name
    :param type: Descriptor type
    :type type: Type
    :param ordered_values: a list of ordered values
    :param unordered_values: a list of values, for which the order does not
        matter
    :param create_new_on: gives the condition for constructing a new variable instead
        of using the new one

    :return_type: a tuple (:class:`~Descriptor`, int)

.. function:: Descriptor.retrieve(name, type, ordered_values, onordered_values[, create_new_on])

    Find and return an existing variable, or :obj:`None` if no match is found.

    :param name: variable name.
    :param type: variable type.
    :type type: Type
    :param ordered_values: a list of ordered values
    :param unordered_values: a list of values, for which the order does not
        matter
    :param create_new_on: gives the condition for constructing a new variable instead
        of using the new one

    :return_type: :class:`~Descriptor`

The following examples give the shown results if
executed only once (in a Python session) and in this order.

:func:`make` can be used for the construction of new variables. ::

    >>> v1, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete, ["a", "b"])
    >>> print s, v1.values
    NotFound <a, b>

A new variable was created and the status is
:obj:`~Descriptor.MakeStatus.NotFound`. ::

    >>> v2, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete, ["a"], ["c"])
    >>> print s, v2 is v1, v1.values
    MissingValues True <a, b, c>

The status is :obj:`~Descriptor.MakeStatus.MissingValues`, yet the
variable is reused (``v2 is v1``). ``v1`` gets a new value, ``"c"``,
which was given as an unordered value. It does not matter that the new
variable does not need the value ``b``. ::

    >>> v3, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete, ["a", "b", "c", "d"])
    >>> print s, v3 is v1, v1.values
    MissingValues True <a, b, c, d>

This is like before, except that the new value, ``d`` is not among the
ordered values. ::

    >>> v4, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete, ["b"])
    >>> print s, v4 is v1, v1.values, v4.values
    Incompatible, False, <b>, <a, b, c, d>

The new variable needs to have ``b`` as the first value, so it is
incompatible with the existing variables. The status is
:obj:`~Descriptor.MakeStatus.Incompatible` and a new variable is
created; the two variables are not equal and have different lists of
values. ::

    >>> v5, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete, None, ["c", "a"])
    >>> print s, v5 is v1, v1.values, v5.values
    OK True <a, b, c, d> <a, b, c, d>

The new variable has values ``c`` and ``a``, but the order is not
important, so the existing attribute is
:obj:`~Descriptor.MakeStatus.OK`. ::

    >>> v6, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete, None, ["e"]) "a"])
    >>> print s, v6 is v1, v1.values, v6.values
    NoRecognizedValues True <a, b, c, d, e> <a, b, c, d, e>

The new variable has different values than the existing variable
(status is :obj:`~Descriptor.MakeStatus.NoRecognizedValues`), but the
existing one is nonetheless reused. Note that we gave ``e`` in the
list of unordered values. If it was among the ordered, the reuse would
fail. ::

    >>> v7, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete, None,
            ["f"], Orange.feature.MakeStatus.NoRecognizedValues)))
    >>> print s, v7 is v1, v1.values, v7.values
    Incompatible False <a, b, c, d, e> <f>

This is the same as before, except that we prohibited reuse when there
are no recognized values. Hence a new variable is created, though the
returned status is the same as before::

    >>> v8, s = Orange.feature.Descriptor.make("a", Orange.feature.Type.Discrete,
            ["a", "b", "c", "d", "e"], None, Orange.feature.MakeStatus.OK)
    >>> print s, v8 is v1, v1.values, v8.values
    OK False <a, b, c, d, e> <a, b, c, d, e>

Finally, this is a perfect match, but any reuse is prohibited, so a
new variable is created.



Variables computed from other variables
---------------------------------------

Values of variables are often computed from other variables, for
instance in. The mechanism described below usually functions behind
the scenes, so understanding it is required only for implementing
specific transformations.

Monk 1 is a well-known dataset with target concept ``y := a==b or e==1``.
It can help the learning algorithm if the four-valued attribute ``e`` is
replaced with a binary attribute having values `"1"` and `"not 1"`. The
new variable will be computed from the old one on the fly.

.. literalinclude:: code/variable-get_value_from.py
    :lines: 7-17

The new variable is named ``e2``; we define it with a descriptor of
type :obj:`Discrete`, with appropriate name and values ``"not 1"`` and
``1`` (we chose this order so that the ``not 1``'s index is ``0``,
which can be, if needed, interpreted as ``False``). Finally, we tell
e2 to use ``checkE`` to compute its value when needed, by assigning
``checkE`` to ``e2.get_value_from``.

``checkE`` is a function that is passed an instance and another
argument we do not care about here. If the instance's ``e`` equals
``1``, the function returns value ``1``, otherwise it returns ``not
1``. Both are returned as values, not plain strings.

In most circumstances the value of ``e2`` can be computed on the fly -
we can pretend that the variable exists in the data, although it does
not (but can be computed from it). For instance, we can compute the
information gain of variable ``e2`` or its distribution without
actually constructing data containing the new variable.

.. literalinclude:: code/variable-get_value_from.py
    :lines: 19-22

There are methods which cannot compute values on the fly because it
would be too complex or time consuming. In such cases, the data need
to be converted to a new :obj:`Orange.data.Table`::

    new_domain = Orange.data.Domain([data.domain["a"], data.domain["b"], e2, data.domain.class_var])
    new_data = Orange.data.Table(new_domain, data)

Automatic computation is useful when the data is split into training
and testing examples. Training instances can be modified by adding,
removing and transforming variables (in a typical setup, continuous
variables are discretized prior to learning, therefore the original
variables are replaced by new ones). Test instances, on the other
hand, are left as they are. When they are classified, the classifier
automatically converts the testing instances into the new domain,
which includes recomputation of transformed variables.

.. literalinclude:: code/variable-get_value_from.py
    :lines: 24-
