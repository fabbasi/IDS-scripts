.. py:currentmodule:: Orange.data

======================
Data table (``Table``)
======================

Class `Orange.data.Table` holds a list of data instances of type
:obj:`Orange.data.Instance`. All instances belong to the same domain
(:obj:`Orange.data.Domain`).

Data tables are usually loaded from a file (see :doc:`Orange.data.formats`)::

    import Orange
    data = Orange.data.Table("titanic")

Data tables can also be created programmatically, as in the :ref:`code
below <example-table-prog1>`.

:obj:`Table` supports most list-like operations: getting, setting,
removing data instances, as well as methods :obj:`append` and
:obj:`extend`. When setting items, the item must be
either the instance of the correct type or a Python list of
appropriate length and content to be converted into a data instance of
the corresponding domain. Retrieving data instances returns references
and not copies: changing the retrieved instance changes the data in the
table. Slicing returns ordinary Python lists containing references to
data instances, not a new :obj:`Orange.data.Table`.

According to a Python convention, the data table is considered ``False``
when empty.

.. class:: Table

    .. attribute:: domain

        The domain to which the instances belong. This
        attribute is read-only.

    .. attribute:: owns_instances

        ``True`` if the table contains the data instances and ``False`` if
        it contains references to instances owned by another table.

    .. attribute:: owner

        The actual owner of the data when ``own_instances`` is ``False``;
        ``None`` otherwise.

    .. attribute:: version

        An integer that is increased when instances are added or
        removed from the table. It does not detect changes of the data.

    .. attribute:: random_generator

       Random generator that is used by method
       :obj:`random_instance`. If the method is called and
       ``random_generator`` is ``None``, a new generator is constructed
       with random seed 0 and stored here for future use.

    .. attribute:: attribute_load_status

       If the table was loaded from a file, this list of flags tells
       whether the feature descriptors were reused and how they
       matched. See :ref:`descriptor reuse <variable_descriptor_reuse>`
       for details.

    .. attribute:: meta_attribute_load_status

       A dictionary holding this same information for meta
       attributes, with keys corresponding to their ids and values to
       load statuses.

    .. method:: __init__(filename[, create_new_on])

        Read data from the given file. If the name includes the
        extension it must be one of the known file formats
        (see :doc:`/Orange.data.formats`). If no extension is given, the
        directory is searched for any file with recognized extensions. If the
        file is not found, Orange will also search the directories
        specified in the environment variable `ORANGE_DATA_PATH`.

        The optional flag ``create_new_on`` decides when variable
        descriptors are reused. See :ref:`descriptor reuse
        <variable_descriptor_reuse>` for more details.

        :param filename: the name of the file
        :type filename: str
        :param create_new_on: flag specifying when to reuse existing descriptors
        :type create_new_on: int

    .. _example-table-prog1:

    .. method:: __init__(domain)

        Construct an empty data table with the given domain.

        .. literalinclude:: code/datatable1.py
            :lines: 7-16

        The example :ref:`continues <example-table-prog2>`.

        :param domain: domain descriptor
        :type domain: Orange.data.Domain

    .. method:: __init__(instances[, references])

        Construct a new data table containing the given data
        instances. These can be given either as another :obj:`Table`
        or as list of instances represented by list of value or as
        :obj:`Orange.data.Instance`.

        If the optional second argument is ``True``, the first argument
        must be a :obj:`Table`. The new table will contain references
        to data stored in the given table. If the second argument is
        omitted or ``False``, data instances are copied.

        :param instances: data instances
        :type instances: Table or list
        :param references: if ``True``, the new table contains references
        :type references: bool

    .. _example-table-prog2:

    .. method:: __init__(domain, instances)

        Construct a new data table with the given domain and initialize
        it with the given instances. Instances can be given as a
        :obj:`Table` (if domains do not match, they are converted),
        as a list containing either instances of
        :obj:`Orange.data.Instance` or lists.

        This constructor can also be used for conversion from numpy
        arrays. The argument ``instances`` can be a numpy array. The number
        of variables in the domain must match the number of columns.

        :param domain: domain descriptor
        :type domain: Orange.data.Domain
        :param instances: data instances
        :type instances: Table or list or numpy.array

        The following example fills the data table created :ref:`above
        <example-table-prog1>` with some data from a list.

        .. literalinclude:: code/datatable1.py
            :lines: 29-34

        The following example shows initializing a data table from
        numpy array.

        .. literalinclude:: code/datatable1.py
            :lines: 38-41

    .. method:: __init__(tables)

        Construct a table by combining data instances from a list of
        tables. All tables must have the same length. Domains are
        combined so that each (ordinary) feature appears only once in
        the resulting table. The class attribute is the last class
        attribute in the list of tables; for instance, if three tables
        are merged but the last one is class-less, the class attribute
        for the new table will come from the second table. Meta
        attributes for the new domain are merged based on id's: if the
        same attribute appears under two id's it will be added
        twice. If, on the opposite, same id appears two different
        attributes in two tables, this raises an exception. As
        instances are merged, exception is raised if a features or
        a meta attribute that appears in multiple tables does not have the
        same value on all of them; the feature is allowed to have a
        missing value on one or more (or all) tables.

        Note that this is not the SQL's join operator as it doesn't
        try to find matches between the tables but instead merges them
        row by row.

        :param tables: tables to be merged into the new table
        :type tables: list of instances of :obj:`Table`

        For example, suppose the file merge1.tab contains::

            a1    a2    m1    m2
            f     f     f     f
                        meta  meta
            1     2     3     4
            5     6     7     8
            9     10    11    12

        and merge2.tab contains::

            a1    a3    m1     m3
            f     f     f      f
                        meta   meta
            1     2.5   3      4.5
            5     6.5   7      8.5
            9     10.5  11     12.5

        The two tables can be loaded, merged and printed out by the
        following script.

        .. literalinclude:: code/datatable_merge.py

        This is what the output looks like::

            Domain 1:  [a1, a2], {-2:m1, -3:m2}
            Domain 2:  [a1, a3], {-2:m1, -4:m3}
            Merged:    [a1, a2, a3], {-2:m1, -3:m2, -4:m3}

               [1, 2], {"m1":3, "m2":4}
             + [1, 2.5], {"m1":3, "m3":4.5}
            -> [1, 2, 2.5], {"m1":3, "m2":4, "m3":4.5}

               [5, 6], {
            "m1":7, "m2":8}
             + [5, 6.5], {"m1":7, "m3":8.5}
            -> [5, 6, 6.5], {"m1":7, "m2":8, "m3":8.5}

               [9, 10], {"m1":11, "m2":12}
             + [9, 10.5], {"m1":11, "m3":12.5}
            -> [9, 10, 10.5], {"m1":11, "m2":12, "m3":12.5}

        Merging succeeds since the values of `a1` and `m1` are the
        same for all matching instances from both tables.

    .. method:: append(instance)

        Append the given instance to the end of the table.

        :param instance: instance to be appended
        :type instance: :obj:`Orange.data.Instance` or a list

        .. literalinclude:: code/datatable1.py
            :lines: 21-24

    .. method:: extend(instances)

        Append the given list of instances to the end of the table.

        :param instances: instances to be appended
        :type instances: list


    .. method:: select(folds[, select, negate=False])

        Return a subset of instances as a new :obj:`Table`. The first
        argument should be a list of the same length as the table; its
        elements should be integers or bools. The resulting table
        contains instances corresponding to non-zero elements of the
        list.

        If the second argument is given, it must be an integer; method
        ``select`` will then return the data instances for which the
        corresponding ``fold``'s elements match the value of the
        argument ``select``.

        The third argument, `negate` inverts the selection. It can
        only be given as a keyword.

        Note: This method should be used when the selected data
        instances are going to be modified later on. In all other
        cases, method :obj:`select_ref` is preferred.

        :param folds: list of fold indices corresponding to data instances
        :type folds: list
        :param select: select which instances to pick
        :type select: int
        :param negate: inverts the selection
        :type negate: bool
        :rtype: :obj:`Orange.data.Table`

        One common use of this method is to split the data into
        folds. A list for the first argument can be prepared using
        `Orange.data.sample.SubsetIndicesCV`. The following example
        prepares a simple data table and indices for four-fold cross
        validation, and then selects the training and testing sets for
        each fold.

        .. literalinclude:: code/datatable2.py
            :lines: 7-27

        The printout begins with::

            Indices:  <1, 0, 2, 2, 0, 1, 0, 3, 1, 3>

            Fold 0: train
                 [0.000000]
                 [2.000000]
                 [3.000000]
                 [5.000000]
                 [7.000000]
                 [8.000000]
                 [9.000000]

                  : test
                 [1.000000]
                 [4.000000]
                 [6.000000]

        Another form of calling the method is to use a vector of
        zero's and one's.

        .. literalinclude:: code/datatable2.py
            :lines: 29-31

        This prints out::

            [0.000000]
            [1.000000]
            [9.000000]

    .. method:: select_ref(folds[, select, negate=False])

        Same as :obj:`select`, except that the resulting table
        contains references to data instances in the original table
        instead of its own copy of data.

        In most cases, this function is preferred over the former
        since it consumes less memory.

        :param folds: list of fold indices corresponding to data instances
        :type folds: list
        :param select: select which instances to pick
        :type select: int
        :param negate: inverts the selection
        :type negate: bool
        :rtype: :obj:`Orange.data.Table`

    .. method:: get_items(indices)

        Return a table with data instances indicated by indices. For
        instance, `data.get_items([0, 1, 9])` returns a table with
        instances with indices 0, 1 and 9.

        This function is useful when data is going to be modified. If
        not, use :obj:`get_items_ref`.

        :param indices: indices of selected data instances
        :type indices: list of int's
        :rtype: :obj:`Orange.data.Table`

    .. method:: get_items_ref(indices)

         Same as above, except that it returns a table with references
         to data instances. This method is usually
         preferred over the above one.

        :param indices: indices of selected data instances
        :type indices: list of int's
        :rtype: :obj:`Orange.data.Table`

    .. method:: filter(conditions)

        Return a table with data instances matching the
        criteria. These can be given in form of keyword arguments or a
        dictionary; with the latter, additional keyword argument ``negate``
        can be given to reverse the selection.

        Note that method :obj:`filter_ref` is more memory efficient and
        should be preferred when data is not going to be modified.

        Young patients from the lenses data set can be selected by ::

            young = data.filter(age="young")

        More than one value can be allowed and more than one attribute
        checked. This selects all patients with age "young" or "psby" who
        are astigmatic::

            young = data.filter(age=["young", "presbyopic"], astigm="y")

        The following has the same effect::

            young = data.filter({"age": ["young", "presbyopic"], 
                                "astigm": "y"})

        Selection can be reversed only in the latter form, by adding
        a keyword argument ``negate`` with value 1::

            young = data.filter({"age": ["young", "presbyopic"], 
                                "astigm": "y"},
                                negate=1)

        Filters for continuous features are specified by pairs of
        values. In dataset "bridges", bridges with lengths between
        1000 and 2000 (inclusive) are selected by ::

            mid = data.filter(LENGTH=(1000, 2000))

        Bridges that are shorter or longer than that can be selected
        by inverting the range. ::

            mid = data.filter(LENGTH=(2000, 1000))

    .. method:: filter(filt)

            Similar to above, except that conditions are given as
            :obj:`Orange.core.Filter`.

    .. method:: filter_ref(conditions), filter_ref(filter)

            Same as the above two, except that they return a table
            with references to instances instead of their copies.

    .. method:: filter_bool(conditions), filter_bool(filter)

            Return a list of bools denoting which data instances are
            accepted by the conditions or the filter.

    .. method:: translate(domain)

            Return a new data table in which data instances are
            translated into the given domain.
          
            :param domain: new domain
            :type domain: :obj:`Orange.data.Domain`
            :rtype: :obj:`Orange.data.Table`

    .. method:: translate(variables[, keep_metas])

            Similar to above, except that the domain is given by a
            list of features. If ``keep_metas`` is ``True``, the new data
            instances will also have all the meta attributes from the
            original domain.

            :param variables: variables for the new data
            :type variables: list
            :rtype: :obj:`Orange.data.Table`

    .. method:: to_numpy(content, weightID, multinominal)

        Convert a data table to numpy array. Raises an exception if the data
        contains undefined values. :obj:`to_numpyMA` converts to a masked
        array where the mask denotes the defined values. (For conversion
        from numpy, see the constructor.)

        The function returns a tuple with the array and, depending on
        arguments, some vectors. The argument ``content`` is a string
        separated in two parts with a slash. The part to the left of slash
        describes the content of the array; in the part on the right side
        lists the vectors. The content is described with the following
        characters:

        ``a``
            features (without the class); can only appear on the left

        ``A``
            like ``a``, but raises exception if there are no features

        ``c``
            class value represented as an index of the value (0, 1, 2...);
            if the data has no class, the column is omitted (if ``c`` is to
            the left of the slash) or the tuple will contain ``None``
            instead of the vector.

        ``C``
            like ``c``, but raises exception if the data has no class

        ``w``
            instance weight; like for ``c`` the column is omitted or
            ``None`` is returned instead of the vector if the argument
            ``weightID`` is missing.

        ``W``
            instance weight; raise an exception if ``weightID``
            is missing.

        ``0``
            a vector of zeros

        ``1``
            a vector of ones

	The default content is ``a/cw``: an array with feature values and
	separate vectors with classes and weights. Specifying an empty string
	has the same effect. If the elements to the right of the slash repeat,
	the function returns the same Python object, e.g. in ``acc000/cwww`` the
	three weight vectors are one and the same Python object, so modifying
	one will change all three of them.

        This is the default behaviour on data set iris with 150 data
        instances described by four features and a class value::

	    >>> data = orange.ExampleTable("../datasets/iris")
	    >>> a, c, w = data.toNumpy()
	    >>> a.shape
	    (150, 4)
	    >>> c.shape
	    (150,)
	    >>> print w
            None
	    >>> a[0]
	    array([ 5.0999999 ,  3.5       ,  1.39999998,  0.2       ])
	    >>> c[0]
	    0.0

        For a more complicated example, the array will contain a column with
        class, features, a vector of ones, two vectors with classes and
        another vector of zeroes::

	    >>> a, = data.toNumpy("ca1cc0")
	    >>> a[0]
	    array([ 0., 5.0999999, 3.5       , 1.39999998, 0.2       , 1., 0., 0., 0.])
	    >>> a[130]
	    array([ 2., 7.4000001, 2.79999995, 6.0999999 , 1.89999998, 1., 2., 2., 0.])
	    >>> c[120]
	    2.0

	The third argument specifies the treatment of non-continuous
	non-binary values (binary values are always translated to 0.0 or
	1.0). The argument's value can be
	:obj:`Orange.data.Table.Multinomial_Ignore` (such features are
	omitted), :obj:`Orange.data.Table.Multinomial_AsOrdinal` (the
	values' indices are treated as continuous numbers) or
	:obj:`Orange.data.Table.Multinomial_Error` (an exception is raised
	if such features are encountered). Default treatment is
	:obj:`Orange.data.Table.ExampleTable.Multinomial_AsOrdinal`.

	When the class attribute is discrete and has more than two values,
	an exception is raised unless multinomial attributes are treated as
	ordinal. More options for treating multinominal values are available
	in :obj:`Orange.data.continuization`.

    .. method:: to_numpyMA(content, weightID, multinominal)

        Similar to :obj:`to_numpy` except that it returns a masked array
        with mask representing the (un)defined values.

    .. method:: checksum()

            Return a CRC32 computed over all discrete and continuous
            features and class attributes of all data instances.

            :rtype: int

    .. method:: has_missing_values()

            Return ``True`` if any of data instances has any missing
            values. Meta attributes are not checked.

    .. method:: has_missing_classes()

            Return ``True`` if any instance miss the class value.

    .. method:: random_instance()

            Return a random instance from the
            table. Data table's :obj:`random_generator` is used,
            which is initially seeded to 0, so results are
            deterministic.

    .. method:: remove_duplicates([weightID])

            Remove duplicates of data instances. If ``weightID`` is given,
            a meta attribute is added which contains the number of
            instances merged into each new instance.

            :param weightID: id for meta attribute with weight
            :type weightID: int
            :rtype: None

    .. method:: sort([variables])

            Sort the data table. The argument gives the
            values ordered by importance. If omitted, the order from
            the domain is used. Values of discrete
            features are not ordered alphabetically but according to
            the :obj:`Orange.feature.Discrete.values`.

            This sorts the data from the bridges data set by the lengths
            and years of their construction::

                data.sort(["LENGTH", "ERECTED"])

    .. method:: shuffle()

            Randomly shuffle the data instances.

    .. method:: add_meta_attribute(attr[, value=1])

            Add a meta value to all data instances. The first argument
            can be an integer id, or a string or a variable descriptor
            of a meta attribute registered in the domain.

    .. method:: remove_meta_attribute(attr)

            Remove a meta attribute from all data instances.


