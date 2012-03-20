"""\
====================================================
Multivariate Adaptive Regression Splines (``earth``)
====================================================

.. index:: regression, linear model

`Multivariate adaptive regression splines (MARS)`_ is a non-parametric
regression method that extends a linear model with non-linear
interactions.

This module borrows the implementation of the technique from the `Earth R 
package`_ by Stephen Milborrow. 

.. _`Multivariate adaptive regression splines (MARS)`: http://en.wikipedia.org/wiki/Multivariate_adaptive_regression_splines
.. _`Earth R package`: http://cran.r-project.org/web/packages/earth/index.html

Example ::

    >>> import Orange
    >>> data = Orange.data.Table("housing")
    >>> c = Orange.regression.earth.EarthLearner(data, degree=2, terms=10)
    >>> print c
    MEDV =
       23.587
       +11.896 * max(0, RM - 6.431)
       +1.142 * max(0, 6.431 - RM)
       -0.612 * max(0, LSTAT - 6.120)
       -228.795 * max(0, NOX - 0.647) * max(0, RM - 6.431)
       +0.023 * max(0, TAX - 307.000) * max(0, 6.120 - LSTAT)
       +0.029 * max(0, 307.000 - TAX) * max(0, 6.120 - LSTAT)


.. autoclass:: EarthLearner
    :members:

.. autoclass:: EarthClassifier
    :members:


Utility functions
-----------------

.. autofunction:: gcv

.. autofunction:: plot_evimp

.. autofunction:: bagged_evimp

.. autoclass:: ScoreEarthImportance

"""

import Orange
from Orange.feature import Discrete, Continuous
from Orange.data import Table, Domain
from Orange.preprocess import Preprocessor_continuize, \
                              Preprocessor_impute, \
                              Preprocessor_preprocessorList, \
                              DomainContinuizer

import numpy

def is_discrete(var):
    return isinstance(var, Discrete)

def is_continuous(var):
    return isinstance(var, Continuous)

def expand_discrete(var):
    """ Expand a discrete variable ``var`` returning one continuous indicator
    variable for each value of ``var`` (if the number of values is grater
    then 2 else return only one indicator variable).
    
    """
    if len(var.values) > 2:
        values = var.values
    elif len(var.values) == 2:
        values = var.values[-1:]
    else:
        values = var.values[:1]
    new_vars = []
    for value in values:
        new = Continuous("{0}={1}".format(var.name, value))
        new.get_value_from = cls = Orange.core.ClassifierFromVar(whichVar=var)
        cls.transformer = Orange.core.Discrete2Continuous()
        cls.transformer.value = int(Orange.core.Value(var, value))
        new.source_variable = var
        new_vars.append(new)
    return new_vars

def select_attrs(table, features, class_var=None,
                 class_vars=None, metas=None):
    """ Select only ``attributes`` from the ``table``.
    """
    if class_vars is None:
        domain = Domain(features, class_var)
    else:
        domain = Domain(features, class_var, class_vars=class_vars)
    if metas:
        domain.add_metas(metas)
    return Table(domain, table)
    
class EarthLearner(Orange.regression.base.BaseRegressionLearner):
    """Earth learner class. Supports both regression and classification
    problems. In case of classification the class values are expanded into 
    continuous indicator columns (one for each value if the number of 
    values is grater then 2), and a multi response model is learned on these
    new columns. The resulting classifier will then use the computed response
    values on new instances to select the final predicted class.
     
    """
    def __new__(cls, instances=None, weight_id=None, **kwargs):
        self = Orange.regression.base.BaseRegressionLearner.__new__(cls)
        if instances is not None:
            self.__init__(**kwargs)
            return self.__call__(instances, weight_id)
        else:
            return self
        
    def __init__(self, degree=1, terms=21, penalty= None, thresh=1e-3,
                 min_span=0, new_var_penalty=0, fast_k=20, fast_beta=1,
                 pruned_terms=None, scale_resp=True, store_instances=True,
                **kwds):
        """Initialize the learner instance.
        
        :param degree: Maximum degree (num. of hinge functions per term)
            of the terms in the model.
        :type degree: int
        :param terms: Maximum number of terms in the forward pass (default 21).
            
            .. note:: If this paramter is None then 
                ``min(200, max(20, 2 * n_attributes)) + 1`` will be used. This
                is the same as the default setting in earth R package.
                
        :type terms: int
        :param penalty: Penalty for hinges in the GCV computation (used 
            in the pruning pass). By default it is 3.0 if the degree > 1,
            2.0 otherwise. 
        :type penalty: float
        :param thresh: Threshold for RSS decrease in the forward pass
            (default 0.001).
        :type thresh: float
        :param min_span: TODO.
        :param new_var_penalty: Penalty for introducing a new variable
            in the model during the forward pass (default 0).
        :type new_var_penalty: float
        :param fast_k: Fast k.
        :param fast_beta: Fast beta.
        :param pruned_terms: Maximum number of terms in the model after
            pruning (default None - no limit).
        :type pruned_terms: int
        :param scale_resp: Scale responses prior to forward pass (default
            True - ignored for multi response models).
        :type scale_resp: bool
        :param store_instances: Store training instances in the model
            (default True).
        :type store_instances: bool
         
        .. todo:: min_span, prunning_method (need Leaps like functionality,
            currently only eval_subsets_using_xtx is implemented). 
        
        """
        
        super(EarthLearner, self).__init__()
        
        self.degree = degree
        self.terms = terms
        if penalty is None:
            penalty = 3 if degree > 1 else 2
        self.penalty = penalty 
        self.thresh = thresh
        self.min_span = min_span
        self.new_var_penalty = new_var_penalty
        self.fast_k = fast_k
        self.fast_beta = fast_beta
        self.pruned_terms = pruned_terms
        self.scale_resp = scale_resp
        self.store_instances = store_instances
        self.__dict__.update(kwds)
        
        self.continuizer.class_treatment = DomainContinuizer.Ignore
        
    def __call__(self, instances, weight_id=None):
        
        expanded_class = None
        multitarget = False
        
        if instances.domain.class_var:
            instances = self.impute_table(instances)
            instances = self.continuize_table(instances)
            
            if is_discrete(instances.domain.class_var):
                # Expand a discrete class with indicator columns
                expanded_class = expand_discrete(instances.domain.class_var)
                y_table = select_attrs(instances, expanded_class)
                (y, ) = y_table.to_numpy_MA("A")
                (x, ) = instances.to_numpy_MA("A")
            elif is_continuous(instances.domain.class_var):
                x, y, _ = instances.to_numpy_MA()
                y = y.reshape((-1, 1))
            else:
                raise ValueError("Cannot handle the response.")
        elif instances.domain.class_vars:
            # Multi-target domain
            if not all(map(is_continuous, instances.domain.class_vars)):
                raise TypeError("Only continuous multi-target classes are supported.")
            x_table = select_attrs(instances, instances.domain.attributes)
            y_table = select_attrs(instances, instances.domain.class_vars)
            
            # Impute and continuize only the x_table
            x_table = self.impute_table(x_table)
            x_table = self.continuize_table(x_table)
            domain = Domain(x_table.domain.attributes,
                            class_vars=instances.domain.class_vars)
            
            (x, ) = x_table.to_numpy_MA("A")
            (y, ) = y_table.to_numpy_MA("A")
            
            multitarget = True
        else:
            raise ValueError("Class variable expected.")
        
        if self.scale_resp and y.shape[1] == 1:
            sy = y - numpy.mean(y, axis=0)
            sy = sy / numpy.std(sy, axis=1)
        else:
            sy = y
            
        terms = self.terms
        if terms is None:
            # Automatic maximum number of terms
            terms = min(200, max(20, 2 * x.shape[1])) + 1
            
        n_terms, used, bx, dirs, cuts = forward_pass(x, sy,
            degree=self.degree, terms=terms, penalty=self.penalty,
            thresh=self.thresh, fast_k=self.fast_k, fast_beta=self.fast_beta,
            new_var_penalty=self.new_var_penalty)
        
        # discard unused terms from bx, dirs, cuts
        bx = bx[:, used]
        dirs = dirs[used, :]
        cuts = cuts[used, :]
        
        # pruning
        used, subsets, rss_per_subset, gcv_per_subset = \
            pruning_pass(bx, y, self.penalty,
                         pruned_terms=self.pruned_terms)
        
        # Fit betas
        bx_used = bx[:, used]
        betas, res, rank, s = numpy.linalg.lstsq(bx_used, y)
        
        return EarthClassifier(instances.domain, used, dirs, cuts, betas.T,
                               subsets, rss_per_subset, gcv_per_subset,
                               instances=instances if self.store_instances else None,
                               multitarget=multitarget,
                               expanded_class=expanded_class
                               )


def soft_max(values):
    values = numpy.asarray(values)
    return numpy.exp(values) / numpy.sum(numpy.exp(values))


class EarthClassifier(Orange.core.ClassifierFD):
    """ Earth classifier.
    """
    def __init__(self, domain, best_set, dirs, cuts, betas, subsets=None,
                 rss_per_subset=None, gcv_per_subset=None, instances=None,
                 multitarget=False, expanded_class=None,
                 original_domain=None, **kwargs):
        self.multitarget = multitarget
        self.domain = domain
        self.class_var = domain.class_var
        if self.multitarget:
            self.class_vars = domain.class_vars
            
        self.best_set = best_set
        self.dirs = dirs
        self.cuts = cuts
        self.betas = betas
        self.subsets = subsets
        self.rss_per_subset = rss_per_subset
        self.gcv_per_subset = gcv_per_subset
        self.instances = instances
        self.expanded_class = expanded_class
        self.original_domain = original_domain
        self.__dict__.update(kwargs)
        
    def __call__(self, instance, result_type=Orange.core.GetValue):
        if self.multitarget and self.domain.class_vars:
            resp_vars = list(self.domain.class_vars)
        elif is_discrete(self.class_var):
            resp_vars = self.expanded_class
        else:
            resp_vars = [self.class_var]
            
        vals = self.predict(instance)
        vals = [var(val) for var, val in zip(resp_vars, vals)]
        
        from Orange.statistics.distribution import Distribution
        
        if not self.multitarget and is_discrete(self.class_var):
            dist = Distribution(self.class_var)
            if len(self.class_var.values) == 2:
                probs = [1 - float(vals[0]), float(vals[0])]
            else:
                probs = soft_max(map(float, vals))
                
            for val, p in zip(self.class_var.values, probs):
                dist[val] = p
            value = dist.modus()
            vals, probs = [value], [dist]
        else:
            probs = []
            for var, val in zip(resp_vars, vals):
                dist = Distribution(var)
                dist[val] = 1.0
                probs.append(dist)
            
        if not self.multitarget:
            vals, probs = vals[0], probs[0]
            
        if result_type == Orange.core.GetValue:
            return vals
        elif result_type == Orange.core.GetBoth:
            return vals, probs
        else:
            return probs
        
    def base_matrix(self, instances=None):
        """Return the base matrix (bx) of the Earth model for the table.
        If table is not supplied the base matrix of the training instances 
        is returned.
        Base matrix is a len(instances) x num_terms matrix of computed values
        of terms in the model (not multiplied by beta) for each instance.
        
        :param instances: Input instances for the base matrix.
        :type instances: :class:`Orange.data.Table` 
        
        """
        if instances is None:
            instances = self.instances
        instances = select_attrs(instances, self.domain.attributes)
        (data,) = instances.to_numpy_MA("A")
        bx = base_matrix(data, self.best_set, self.dirs, self.cuts)
        return bx
    
    def predict(self, instance):
        """ Predict the response values for the instance
        
        :param instance: Data instance
        :type instance: :class:`Orange.data.Instance`
        
        """
        data = Orange.data.Table(self.domain, [instance])
        bx = self.base_matrix(data)
        bx_used = bx[:, self.best_set]
        vals = numpy.dot(bx_used, self.betas.T).ravel()
        return vals
    
    def used_attributes(self, term=None):
        """ Return the used terms for term (index). If no term is given
        return all attributes in the model.
        
        :param term: term index
        :type term: int
        
        """
        if term is None:
            return reduce(set.union, [self.used_attributes(i) \
                                      for i in range(self.best_set.size)],
                          set())
            
        attrs = self.domain.attributes
        
        used_mask = self.dirs[term, :] != 0.0
        return [a for a, u in zip(attrs, used_mask) if u]
    
    def evimp(self, used_only=True):
        """ Return the estimated variable importances.
        
        :param used_only: if True return only used attributes
        
        """  
        return evimp(self, used_only)
    
    def __reduce__(self):
        return (type(self), (self.domain, self.best_set, self.dirs,
                            self.cuts, self.betas),
                dict(self.__dict__))
        
    def to_string(self, percision=3, indent=3):
        """ Return a string representation of the model.
        """
        return format_model(self, percision, indent)
        
    def __str__(self):
        return self.to_string()
    

"""
Utility functions
-----------------
"""
    
def base_matrix(data, best_set, dirs, cuts):
    """ Return the base matrix for the earth model.
    
    :param data: Input data
    :type data: :class:`numpy.ndarray`
    
    :param best_set: A array of booleans indicating used terms.
    :type best_set: :class:`numpy.ndarray`
    
    :param dirs: Earth model's dirs members
    :type dirs: :class:`numpy.ndarray`
    
    :param cuts: Earth model's cuts members
    :type cuts: :class:`numpy.ndarray`
    
    """
    data = numpy.asarray(data)
    best_set = numpy.asarray(best_set)
    dirs = numpy.asarray(dirs)
    cuts = numpy.asarray(cuts)
    
    bx = numpy.zeros((data.shape[0], best_set.shape[0]))
    bx[:, 0] = 1.0 # The intercept
    for termi in range(1, best_set.shape[0]):
        term_dirs = dirs[termi]
        term_cuts = cuts[termi]
        
        dir_p1 = numpy.where(term_dirs == 1)[0]
        dir_m1 = numpy.where(term_dirs == -1)[0]
        dir_2 = numpy.where(term_dirs == 2)[0]
        
        x1 = data[:, dir_p1] - term_cuts[dir_p1]
        x2 = term_cuts[dir_m1] - data[:, dir_m1]
        x3 = data[:, dir_2]
        
        x1 = numpy.where(x1 > 0.0, x1, 0.0)
        x2 = numpy.where(x2 > 0.0, x2, 0.0)
        
        X = numpy.hstack((x1, x2, x3))
        X = numpy.cumprod(X, axis=1)
        bx[:, termi] = X[:, -1] if X.size else 0.0
        
    return bx

    
def gcv(rss, n, n_effective_params):
    """ Return the generalized cross validation.
    
    .. math:: gcv = rss / (n * (1 - NumEffectiveParams / n) ^ 2)
    
    :param rss: Residual sum of squares.
    :param n: Number of training instances.
    :param n_effective_params: Number of effective paramaters.
     
    """
    return  rss / (n * (1. - n_effective_params / n) ** 2)

"""
Multi-label utility functions
"""


"""
ctypes interface to ForwardPass and EvalSubsetsUsingXtx.
"""
        
import ctypes
from numpy import ctypeslib
import orange

_c_orange_lib = ctypeslib.load_library(orange.__file__, "")
_c_forward_pass_ = _c_orange_lib.EarthForwardPass

_c_forward_pass_.argtypes = \
    [ctypes.POINTER(ctypes.c_int),  #pnTerms:
     ctypeslib.ndpointer(dtype=ctypes.c_bool, ndim=1),  #FullSet
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"), #bx
     ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=2, flags="F_CONTIGUOUS"),    #Dirs
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"), #Cuts
     ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=1),  #nFactorsInTerms
     ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=1),  #nUses
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"), #x
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"), #y
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=1), # Weights
     ctypes.c_int,  #nCases
     ctypes.c_int,  #nResp
     ctypes.c_int,  #nPred
     ctypes.c_int,  #nMaxDegree
     ctypes.c_int,  #nMaxTerms
     ctypes.c_double,   #Penalty
     ctypes.c_double,   #Thresh
     ctypes.c_int,  #nFastK
     ctypes.c_double,   #FastBeta
     ctypes.c_double,   #NewVarPenalty
     ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=1),  #LinPreds
     ctypes.c_bool, #UseBetaCache
     ctypes.c_char_p    #sPredNames
     ]
    
def forward_pass(x, y, degree=1, terms=21, penalty=None, thresh=0.001,
                  fast_k=21, fast_beta=1, new_var_penalty=2):
    """ Do earth forward pass.
    """
    x = numpy.asfortranarray(x, dtype=ctypes.c_double)
    y = numpy.asfortranarray(y, dtype=ctypes.c_double)
    if x.shape[0] != y.shape[0]:
        raise ValueError("First dimensions of x and y must be the same.")
    if y.ndim == 1:
        y = y.reshape((-1, 1), order="F")
    if penalty is None:
        penalty = 2
    n_cases = x.shape[0]
    n_preds = x.shape[1]
    
    n_resp = y.shape[1] if y.ndim == 2 else y.shape[0]
    
    # Output variables
    n_term = ctypes.c_int()
    full_set = numpy.zeros((terms,), dtype=ctypes.c_bool, order="F")
    bx = numpy.zeros((n_cases, terms), dtype=ctypes.c_double, order="F")
    dirs = numpy.zeros((terms, n_preds), dtype=ctypes.c_int, order="F")
    cuts = numpy.zeros((terms, n_preds), dtype=ctypes.c_double, order="F")
    n_factors_in_terms = numpy.zeros((terms,), dtype=ctypes.c_int, order="F")
    n_uses = numpy.zeros((n_preds,), dtype=ctypes.c_int, order="F")
    weights = numpy.ones((n_cases,), dtype=ctypes.c_double, order="F")
    lin_preds = numpy.zeros((n_preds,), dtype=ctypes.c_int, order="F")
    use_beta_cache = True
    
    # These tests are performed in ForwardPass, and if they fail the function
    # calls exit. So we must check it here and raise a exception to avoid a
    # process shutdown.
    if n_cases < 8:
        raise ValueError("Need at least 8 data instances.")
    if n_cases > 1e8:
        raise ValueError("To many data instances.")
    if n_resp < 1:
        raise ValueError("No response column.")
    if n_resp > 1e6:
        raise ValueError("To many response columns.")
    if n_preds < 1:
        raise ValueError("No predictor columns.")
    if n_preds > 1e5:
        raise ValueError("To many predictor columns.")
    if degree <= 0 or degree > 100:
        raise ValueError("Invalid 'degree'.")
    if terms < 3 or terms > 10000:
        raise ValueError("'terms' must be in >= 3 and <= 10000.")
    if penalty < 0 and penalty != -1:
        raise ValueError("Invalid 'penalty' (the only legal negative value is -1).")
    if penalty > 1000:
        raise ValueError("Invalid 'penalty' (must be <= 1000).")
    if thresh < 0.0 or thresh >= 1.0:
        raise ValueError("Invalid 'thresh' (must be in [0.0, 1.0) ).")
    if fast_beta < 0 or fast_beta > 1000:
        raise ValueError("Invalid 'fast_beta' (must be in [0, 1000] ).")
    if new_var_penalty < 0 or new_var_penalty > 10:
        raise ValueError("Invalid 'new_var_penalty' (must be in [0, 10] ).")
    if (numpy.var(y, axis=0) <= 1e-8).any():
        raise ValueError("Variance of y is zero (or near zero).")
     
    _c_forward_pass_(ctypes.byref(n_term), full_set, bx, dirs, cuts,
                     n_factors_in_terms, n_uses, x, y, weights, n_cases,
                     n_resp, n_preds, degree, terms, penalty, thresh,
                     fast_k, fast_beta, new_var_penalty, lin_preds, 
                     use_beta_cache, None)
    return n_term.value, full_set, bx, dirs, cuts


_c_eval_subsets_xtx = _c_orange_lib.EarthEvalSubsetsUsingXtx

_c_eval_subsets_xtx.argtypes = \
    [ctypeslib.ndpointer(dtype=ctypes.c_bool, ndim=2, flags="F_CONTIGUOUS"),   #PruneTerms
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=1),   #RssVec
     ctypes.c_int,  #nCases
     ctypes.c_int,  #nResp
     ctypes.c_int,  #nMaxTerms
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),   #bx
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),   #y
     ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=1)  #WeightsArg
     ]
    
_c_eval_subsets_xtx.restype = ctypes.c_int

def subset_selection_xtx(X, Y):
    """ Subsets selection using EvalSubsetsUsingXtx in the Earth package.
    """
    X = numpy.asfortranarray(X, dtype=ctypes.c_double)
    Y = numpy.asfortranarray(Y, dtype=ctypes.c_double)
    if Y.ndim == 1:
        Y = Y.reshape((-1, 1), order="F")
        
    if X.shape[0] != Y.shape[0]:
        raise ValueError("First dimensions of bx and y must be the same")
        
    var_count = X.shape[1]
    resp_count = Y.shape[1]
    cases = X.shape[0]
    subsets = numpy.zeros((var_count, var_count), dtype=ctypes.c_bool,
                              order="F")
    rss_vec = numpy.zeros((var_count,), dtype=ctypes.c_double, order="F")
    weights = numpy.ones((cases,), dtype=ctypes.c_double, order="F")
    
    rval = _c_eval_subsets_xtx(subsets, rss_vec, cases, resp_count, var_count,
                        X, Y, weights)
    if rval != 0:
        raise numpy.linalg.LinAlgError("Lin. dep. terms in X")
    
    subsets_ind = numpy.zeros((var_count, var_count), dtype=int)
    for i, used in enumerate(subsets.T):
        subsets_ind[i, :i + 1] = numpy.where(used)[0]
        
    return subsets_ind, rss_vec
    
def subset_selection_xtx_numpy(X, Y):
    """ A numpy implementation of EvalSubsetsUsingXtx in the Earth package.
    Using numpy.linalg.lstsq
    
    """
    X = numpy.asarray(X)
    Y = numpy.asarray(Y)
    
    var_count = X.shape[1]
    rss_vec = numpy.zeros(var_count)
    working_set = range(var_count)
    subsets = numpy.zeros((var_count, var_count), dtype=int)
    
    for subset_size in reversed(range(var_count)):
        subsets[subset_size, :subset_size + 1] = working_set
        X_work = X[:, working_set]
        b, res, rank, s = numpy.linalg.lstsq(X_work, Y)
        if res.size > 0:
            rss_vec[subset_size] = numpy.sum(res)
        else:
            rss_vec[subset_size] = numpy.sum((Y - numpy.dot(X_work, b)) ** 2)
            
        XtX = numpy.dot(X_work.T, X_work)
        iXtX = numpy.linalg.pinv(XtX)
        diag = numpy.diag(iXtX).reshape((-1, 1))
        
        if subset_size == 0:
            break
        
        delta_rss = b ** 2 / diag
        delta_rss = numpy.sum(delta_rss, axis=1)
        delete_i = numpy.argmin(delta_rss[1:]) + 1 # Keep the intercept
        del working_set[delete_i]
    return subsets, rss_vec
    
def subset_selection_xtx2(X, Y):
    """ Another implementation (this uses qr decomp).
    """
    from Orange.misc import linalg
    X = numpy.asfortranarray(X, dtype=ctypes.c_double)
    Y = numpy.asfortranarray(Y, dtype=ctypes.c_double)
    col_count = X.shape[1]
    working_set = range(col_count)
    subsets = numpy.zeros((col_count, col_count), dtype=int)
    rss_vec = numpy.zeros((col_count,))
    QR, k, _, jpvt = linalg.qr_decomp(X)
    
    if k < col_count:
        # remove jpvt[k:] from the work set. Will have zero 
        # entries in the subsets matrix, and inf rss
        for i in sorted(jpvt[k:], reverse=True):
            del working_set[i]
            rss_vec[len(working_set)] = float("inf")
        col_count = len(working_set)
        
    for subset_size in reversed(range(col_count)):
        subsets[subset_size, :subset_size + 1] = working_set
        X_work = X[:, working_set]
        b, rsd, rank = linalg.qr_lstsq(X_work, Y)
        rss_vec[subset_size] = numpy.sum(rsd ** 2)
        XtX = numpy.dot(X_work.T, X_work)
        iXtX = numpy.linalg.pinv(XtX)
        diag = numpy.diag(iXtX)
        
        if subset_size == 0:
            break
        
        delta_rss = b ** 2 / diag
        delete_i = numpy.argmin(delta_rss[1:]) + 1 # Keep the intercept
        del working_set[delete_i]
    return subsets, rss_vec
    
def pruning_pass(bx, y, penalty, pruned_terms=-1):
    """ Do pruning pass
    
    .. todo:: pruned_terms, Leaps
    
    """
    try:
        subsets, rss_vec = subset_selection_xtx(bx, y)
    except numpy.linalg.LinAlgError:
        subsets, rss_vec = subset_selection_xtx_numpy(bx, y)
    
    cases, terms = bx.shape
    n_effective_params = numpy.arange(terms) + 1.0
    n_effective_params += penalty * (n_effective_params - 1.0) / 2.0
    
    gcv_vec = gcv(rss_vec, cases, n_effective_params)
    
    min_i = numpy.argmin(gcv_vec)
    used = numpy.zeros((terms), dtype=bool)
    
    used[subsets[min_i, :min_i + 1]] = True
    
    return used, subsets, rss_vec, gcv_vec

"""
Printing functions.
"""
    
def format_model(model, percision=3, indent=3):
    """ Return a formated string representation of the earth model.
    """
    if model.multitarget:
        r_vars = list(model.domain.class_vars)
    elif is_discrete(model.class_var):
        r_vars = model.expanded_class
    else:
        r_vars = [model.class_var]
        
    r_names = [v.name for v in r_vars]
    betas = model.betas
        
    resp = []
    for name, betas in zip(r_names, betas):
        resp.append(_format_response(model, name, betas,
                                     percision, indent))
    return "\n\n".join(resp)

def _format_response(model, resp_name, betas, percision=3, indent=3):
    header = "%s =" % resp_name
    indent = " " * indent
    fmt = "%." + str(percision) + "f"
    terms = [([], fmt % betas[0])]
    beta_i = 0
    for i, used in enumerate(model.best_set[1:], 1):
        if used:
            beta_i += 1
            beta = fmt % abs(betas[beta_i])
            knots = [_format_knot(model, attr.name, d, c, percision) \
                     for d, c, attr in \
                     zip(model.dirs[i], model.cuts[i], model.domain.attributes) \
                     if d != 0]
            term_attrs = [a for a, d in zip(model.domain.attributes, model.dirs[i]) \
                          if d != 0]
            term_attrs = sorted(term_attrs)
            sign = "-" if betas[beta_i] < 0 else "+"
            if knots:
                terms.append((term_attrs,
                              sign + " * ".join([beta] + knots)))
            else:
                terms.append((term_attrs, sign + beta))
    # Sort by len(term_attrs), then by term_attrs
    terms = sorted(terms, key=lambda t: (len(t[0]), t[0]))
    return "\n".join([header] + [indent + t for _, t in terms])
        
def _format_knot(model, name, dir, cut, percision=3):
    fmt = "%%.%if" % percision
    if dir == 1:
        txt = ("max(0, %s - " + fmt + ")") % (name, cut)
    elif dir == -1:
        txt = ("max(0, " + fmt + " - %s)") % (cut, name)
    elif dir == 2:
        txt = name
    return txt

    
"""\
Variable importance estimation
------------------------------
"""

from collections import defaultdict

def collect_source(vars):
    """ Given a list of variables ``var``, return a mapping from source
    variables (``source_variable`` or ``get_value_from.variable`` members)
    back to the variables in ``vars`` (assumes the default preprocessor in
    EarthLearner).
    
    """
    source = defaultdict(list)
    for var in vars:
        svar = None
        if var.source_variable:
            source[var.source_variable].append(var)
        elif isinstance(var.get_value_from, Orange.core.ClassifierFromVar):
            source[var.get_value_from.variable].append(var)
        elif isinstance(var.get_value_from, Orange.core.ImputeClassifier):
            source[var.get_value_from.classifier_from_var.variable].append(var)
        else:
            source[var].append(var)
    return dict(source)

def map_to_source_var(var, sources):
    """ 
    """
    if var in sources:
        return var
    elif var.source_variable in sources:
        return var.source_variable
    elif isinstance(var.get_value_from, Orange.core.ClassifierFromVar):
        return map_to_source_var(var.get_value_from.variable, sources)
    elif isinstance(var.get_value_from, Orange.core.ImputeClassifier):
        var = var.get_value_from.classifier_from_var.variable
        return map_to_source_var(var, sources)
    else:
        return None
    
def evimp(model, used_only=True):
    """ Return the estimated variable importance for the model.
    
    :param model: Earth model.
    :type model: `EarthClassifier`
    
    """
    if model.subsets is None:
        raise ValueError("No subsets. Use the learner with 'prune=True'.")
    
    subsets = model.subsets
    n_subsets = numpy.sum(model.best_set)
    
    rss = -numpy.diff(model.rss_per_subset)
    gcv = -numpy.diff(model.gcv_per_subset)
    attributes = list(model.domain.variables)
    
    attr2ind = dict(zip(attributes, range(len(attributes))))
    importances = numpy.zeros((len(attributes), 4))
    importances[:, 0] = range(len(attributes))
    
    for i in range(1, n_subsets):
        term_subset = subsets[i, :i + 1]
        used_attributes = reduce(set.union, [model.used_attributes(term) \
                                             for term in term_subset], set())
        for attr in used_attributes:
            importances[attr2ind[attr]][1] += 1.0
            importances[attr2ind[attr]][2] += gcv[i - 1]
            importances[attr2ind[attr]][3] += rss[i - 1]
    imp_min = numpy.min(importances[:, [2, 3]], axis=0)
    imp_max = numpy.max(importances[:, [2, 3]], axis=0)
    
    #Normalize importances.
    importances[:, [2, 3]] = 100.0 * (importances[:, [2, 3]] \
                            - [imp_min]) / ([imp_max - imp_min])
    
    importances = list(importances)
    # Sort by n_subsets and gcv.
    importances = sorted(importances, key=lambda row: (row[1], row[2]),
                         reverse=True)
    importances = numpy.array(importances)
    
    if used_only:
        importances = importances[importances[:,1] > 0.0]
    
    res = [(attributes[int(row[0])], tuple(row[1:])) for row in importances]
    return res


def plot_evimp(evimp):
    """ Plot the variable importances as returned from
    :obj:`EarthClassifier.evimp` call.
    
    ::

        import Orange
        data = Orange.data.Table("housing")
        c = Orange.regression.earth.EarthLearner(data, degree=3)
        Orange.regression.earth.plot_evimp(c.evimp())

    .. image:: files/earth-evimp.png
     
    The left axis is the nsubsets measure and on the right are the normalized
    RSS and GCV.
    
    """
    from Orange.ensemble.bagging import BaggedClassifier
    if isinstance(evimp, EarthClassifier):
        evimp = evimp.evimp()
    elif isinstance(evimp, BaggedClassifier):
        evimp = bagged_evimp(evimp)
        
    import pylab
    fig = pylab.figure()
    axes1 = fig.add_subplot(111)
    attrs = [a for a, _ in evimp]
    imp = [s for _, s in evimp]
    imp = numpy.array(imp)
    X = range(len(attrs))
    l1 = axes1.plot(X, imp[:, 0], "b-",)
    axes2 = axes1.twinx()
    
    l2 = axes2.plot(X, imp[:, 1], "g-",)
    l3 = axes2.plot(X, imp[:, 2], "r-",)
    
    x_axis = axes1.xaxis
    x_axis.set_ticks(X)
    x_axis.set_ticklabels([a.name for a in attrs], rotation=90)
    
    axes1.yaxis.set_label_text("nsubsets")
    axes2.yaxis.set_label_text("normalized gcv or rss")

    axes1.legend([l1, l2, l3], ["nsubsets", "gcv", "rss"])
    axes1.set_title("Variable importance")
    fig.show()

    
def bagged_evimp(classifier, used_only=True):
    """ Extract combined (average) evimp from an instance of BaggedClassifier
    
    Example::

        from Orange.ensemble.bagging import BaggedLearner
        bc = BaggedLearner(EarthLearner(degree=3, terms=10), data)
        bagged_evimp(bc)

    """
    def assert_type(object, class_):
        if not isinstance(object, class_):
            raise TypeError("Instance of %r expected." % (class_))
    
    from Orange.ensemble.bagging import BaggedClassifier
    
    assert_type(classifier, BaggedClassifier)
    bagged_imp = defaultdict(list)
    attrs_by_name = defaultdict(list)
    for c in classifier.classifiers:
        assert_type(c, EarthClassifier)
        imp = evimp(c, used_only=used_only)
        for attr, score in imp:
            bagged_imp[attr.name].append(score) # map by name
            attrs_by_name[attr.name].append(attr)
            
    for attr, scores in bagged_imp.items():
        scores = numpy.average(scores, axis=0)
        bagged_imp[attr] = tuple(scores)
    
    
    bagged_imp = sorted(bagged_imp.items(),
                        key=lambda t: (t[1][0], t[1][1]),
                        reverse=True)
    
    bagged_imp = [(attrs_by_name[name][0], scores) for name, scores in bagged_imp]
    
    if used_only:
        bagged_imp = [(a, r) for a, r in bagged_imp if r[0] > 0]
    return bagged_imp

"""
High level interface for measuring variable importance
(compatible with Orange.feature.scoring module).

"""
from Orange.feature import scoring
            
class ScoreEarthImportance(scoring.Score):
    """ An :class:`Orange.feature.scoring.Score` subclass.
    Scores features based on their importance in the Earth
    model using ``bagged_evimp``'s function return value.
    
    """
    # Return types  
    NSUBSETS = 0
    RSS = 1
    GCV = 2
    
    handles_discrete = True
    handles_continuous = True
    computes_thresholds = False
    needs = scoring.Score.Generator
    
    def __new__(cls, attr=None, data=None, weight_id=None, **kwargs):
        self = scoring.Score.__new__(cls)
        if attr is not None and data is not None:
            self.__init__(**kwargs)
            # TODO: Should raise a warning, about caching
            return self.__call__(attr, data, weight_id)
        elif not attr and not data:
            return self
        else:
            raise ValueError("Both 'attr' and 'data' arguments expected.")
        
    def __init__(self, t=10, degree=2, terms=10, score_what="nsubsets", cached=True):
        """
        :param t: Number of earth models to train on the data
            (using BaggedLearner).
            
        :param score_what: What to return as a score.
            Can be one of: "nsubsets", "rss", "gcv" or class constants
            NSUBSETS, RSS, GCV.
            
        """
        self.t = t
        self.degree = degree
        self.terms = terms
        if isinstance(score_what, basestring):
            score_what = {"nsubsets":self.NSUBSETS, "rss":self.RSS,
                          "gcv":self.GCV}.get(score_what, None)
                          
        if score_what not in range(3):
            raise ValueError("Invalid  'score_what' parameter.")

        self.score_what = score_what
        self.cached = cached
        self._cache_ref = None
        self._cached_evimp = None
        
    def __call__(self, attr, data, weight_id=None):
        ref = self._cache_ref
        if ref is not None and ref is data:
            evimp = self._cached_evimp
        else:
            from Orange.ensemble.bagging import BaggedLearner
            bc = BaggedLearner(EarthLearner(degree=self.degree,
                            terms=self.terms), t=self.t)(data, weight_id)
            evimp = bagged_evimp(bc, used_only=False)
            self._cache_ref = data
            self._cached_evimp = evimp
        
        evimp = dict(evimp)
        score = evimp.get(attr, None)
        
        if score is None:
            source = collect_source(evimp.keys())
            if attr in source:
                # Return average of source var scores
                return numpy.average([evimp[v][self.score_what] \
                                      for v in source[attr]])
            else:
                raise ValueError("Attribute %r not in the domain." % attr)
        else:
            return score[self.score_what]
    
class ScoreRSS(scoring.Score):
    
    handles_discrete = False
    handles_continuous = True
    computes_thresholds = False
    
    def __new__(cls, attr=None, data=None, weight_id=None, **kwargs):
        self = scoring.Score.__new__(cls)
        if attr is not None and data is not None:
            self.__init__(**kwargs)
            # TODO: Should raise a warning, about caching
            return self.__call__(attr, data, weight_id)
        elif not attr and not data:
            return self
        else:
            raise ValueError("Both 'attr' and 'data' arguments expected.")
        
    def __init__(self):
        self._cache_data = None
        self._cache_rss = None
        
    def __call__(self, attr, data, weight_id=None):
        ref = self._cache_data
        if ref is not None and ref is data:
            rss = self._cache_rss
        else:
            x, y = data.to_numpy_MA("1A/c")
            try:
                subsets, rss = subset_selection_xtx2(x, y)
            except numpy.linalg.LinAlgError:
                subsets, rss = subset_selection_xtx_numpy(x, y)
            rss_diff = -numpy.diff(rss)
            rss = numpy.zeros_like(rss)
            for s_size in range(1, subsets.shape[0]):
                subset = subsets[s_size, :s_size + 1]
                rss[subset] += rss_diff[s_size - 1]
            rss = rss[1:] #Drop the intercept
            self._cache_data = data
            self._cache_rss = rss
            
        index = list(data.domain.attributes).index(attr)
        return rss[index]
    

#from Orange.core import EarthLearner as BaseEarthLearner, \
#                        EarthClassifier as BaseEarthClassifier
#from Orange.misc import member_set
# 
#class _EarthLearner(BaseEarthLearner):
#    """ An earth learner. 
#    """
#    def __new__(cls, data=None, weightId=None, **kwargs):
#        self = BaseEarthLearner.__new__(cls, **kwargs)
#        if data is not None:
#            self.__init__(**kwargs)
#            return self.__call__(data, weightId)
#        return self
#    
#    def __init__(self, max_degree=1, max_terms=21, new_var_penalty=0.0,
#                 threshold=0.001, prune=True, penalty=None, fast_k=20,
#                 fast_beta=0.0, store_examples=True, **kwargs):
#        """ Initialize the learner instance.
#        
#        :param max_degree:
#        """
#        self.max_degree = max_degree
#        self.max_terms = max_terms
#        self.new_var_penalty = new_var_penalty
#        self.threshold = threshold
#        self.prune = prunes
#        if penaty is None:
#            penalty = 2.0 if degree > 1 else 3.0
#        self.penalty = penalty
#        self.fast_k = fast_k
#        self.fast_beta = fast_beta
#        self.store_examples = store_examples
#        
#        for key, val in kwargs.items():
#            setattr(self, key, val)
#    
#    def __call__(self, data, weightId=None):
#        if not data.domain.class_var:
#            raise ValueError("No class var in the domain.")
#        
#        with member_set(self, "prune", False):
#            # We overwrite the prune argument (will do the pruning in python).
#            base_clsf =  BaseEarthLearner.__call__(self, data, weightId)
#        
#        if self.prune:
#            (best_set, betas, rss, subsets, rss_per_subset,
#             gcv_per_subset) = self.pruning_pass(base_clsf, data)
#            
#            return _EarthClassifier(base_clsf, data if self.store_examples else None,
#                                   best_set=best_set, dirs=base_clsf.dirs,
#                                   cuts=base_clsf.cuts,
#                                   betas=betas,
#                                   subsets=subsets,
#                                   rss_per_subset=rss_per_subset,
#                                   gcv_per_subset=gcv_per_subset)
#        else:
#            return _EarthClassifier(base_clsf, data if self.store_examples else None)
#    
#    
#    def pruning_pass(self, base_clsf, examples):
#        """ Prune the terms constructed in the forward pass.
#        (Pure numpy reimplementation)
#        """
#        n_terms = numpy.sum(base_clsf.best_set)
#        n_eff_params = n_terms + self.penalty * (n_terms - 1) / 2.0
#        data, y, _ = examples.to_numpy_MA()
#        data = data.filled(0.0)
#        best_set = numpy.asarray(base_clsf.best_set, dtype=bool)
#        
#        bx = base_matrix(data, base_clsf.best_set,
#                         base_clsf.dirs, base_clsf.cuts,
#                         )
#        
#        bx_used = bx[:, best_set]
#        subsets, rss_per_subset = subsets_selection_xtx(bx_used, y) # TODO: Use leaps like library
#        gcv_per_subset = [gcv(rss, bx.shape[0], i + self.penalty * (i - 1) / 2.0) \
#                              for i, rss in enumerate(rss_per_subset, 1)]
#        gcv_per_subset = numpy.array(gcv_per_subset)
#        
#        best_i = numpy.argmin(gcv_per_subset[1:]) + 1 # Ignore the intercept
#        best_ind = subsets[best_i, :best_i + 1]
#        bs_i = 0
#        for i, b in enumerate(best_set):
#            if b:
#                best_set[i] = bs_i in best_ind
#                bs_i += 1
#                
#        bx_subset = bx[:, best_set]
#        betas, rss, rank, s = numpy.linalg.lstsq(bx_subset, y)
#        return best_set, betas, rss, subsets, rss_per_subset, gcv_per_subset
#    
#        
#class _EarthClassifier(Orange.core.ClassifierFD):
#    def __init__(self, base_classifier=None, examples=None, best_set=None,
#                 dirs=None, cuts=None, betas=None, subsets=None,
#                 rss_per_subset=None,
#                 gcv_per_subset=None):
#        self._base_classifier = base_classifier
#        self.examples = examples
#        self.domain = base_classifier.domain
#        self.class_var = base_classifier.class_var
#        
#        best_set = base_classifier.best_set if best_set is None else best_set
#        dirs = base_classifier.dirs if dirs is None else dirs
#        cuts = base_classifier.cuts if cuts is None else cuts
#        betas = base_classifier.betas if betas is None else betas
#        
#        self.best_set = numpy.asarray(best_set, dtype=bool)
#        self.dirs = numpy.array(dirs, dtype=int)
#        self.cuts = numpy.array(cuts)
#        self.betas = numpy.array(betas)
#        
#        self.subsets = subsets
#        self.rss_per_subset = rss_per_subset
#        self.gcv_per_subset = gcv_per_subset
#        
#    @property
#    def num_terms(self):
#        """ Number of terms in the model (including the intercept).
#        """
#        return numpy.sum(numpy.asarray(self.best_set, dtype=int))
#    
#    @property
#    def max_terms(self):
#        """ Maximum number of terms (as specified in the learning step).
#        """
#        return self.best_set.size
#    
#    @property
#    def num_preds(self):
#        """ Number of predictors (variables) included in the model.
#        """
#        return len(self.used_attributes(term))
#    
#    def __call__(self, example, what=Orange.core.GetValue):
#        value = self.predict(example)
#        if isinstance(self.class_var, Orange.feature.Continuous):
#            value = self.class_var(value)
#        else:
#            value = self.class_var(int(round(value)))
#            
#        dist = Orange.statistics.distribution.Distribution(self.class_var)
#        dist[value] = 1.0
#        if what == Orange.core.GetValue:
#            return value
#        elif what == Orange.core.GetProbabilities:
#            return dist
#        else:
#            return (value, dist)
#    
#    def base_matrix(self, examples=None):
#        """ Return the base matrix (bx) of the Earth model for the table.
#        If table is not supplied the base matrix of the training examples 
#        is returned.
#        
#        
#        :param examples: Input examples for the base matrix.
#        :type examples: Orange.data.Table 
#        
#        """
#        if examples is None:
#            examples = self.examples
#            
#        if examples is None:
#            raise ValueError("base matrix is only available if 'store_examples=True'")
#        
#        if isinstance(examples, Orange.data.Table):
#            data, cls, w = examples.to_numpy_MA()
#            data = data.filled(0.0)
#        else:
#            data = numpy.asarray(examples)
#            
#        return base_matrix(data, self.best_set, self.dirs, self.cuts)
#    
#    def _anova_order(self):
#        """ Return indices that sort the terms into the 'ANOVA' format.
#        """
#        terms = [([], 0)] # intercept
#        for i, used in enumerate(self.best_set[1:], 1):
#            attrs = sorted(self.used_attributes(i))
#            if used and attrs:
#                terms.append((attrs, i))
#        terms = sotred(terms, key=lambda t:(len(t[0]), t[0]))
#        return [i for _, i in terms]
#    
#    def format_model(self, percision=3, indent=3):
#        return format_model(self, percision, indent)
#    
#    def print_model(self, percision=3, indent=3):
#        print self.format_model(percision, indent)
#        
#    def predict(self, ex):
#        """ Return the predicted value (float) for example.
#        """
#        x = Orange.data.Table(self.domain, [ex])
#        x, c, w = x.to_numpy_MA()
#        x = x.filled(0.0)[0]
#        
#        bx = numpy.ones(self.best_set.shape)
#        betas = numpy.zeros_like(self.betas)
#        betas[0] = self.betas[0]
#        beta_i = 0
#        for termi in range(1, len(self.best_set)):
#            dirs = self.dirs[termi]
#            cuts = self.cuts[termi]
#            dir_p1 = numpy.where(dirs == 1)[0]
#            dir_m1 = numpy.where(dirs == -1)[0]
#            dir_2 = numpy.where(dirs == 2)[0]
#            
#            x1 = x[dir_p1] - cuts[dir_p1]
#            x2 = cuts[dir_m1] - x[dir_m1]
#            x3 = x[dir_2]
#            
#            x1 = numpy.maximum(x1, 0.0)
#            x2 = numpy.maximum(x2, 0.0)
#
#            X = numpy.hstack((x1, x2, x3))
#            X = numpy.cumprod(X)
#            
#            bx[termi] = X[-1] if X.size else 0.0
#            if self.best_set[termi] != 0:
#                beta_i += 1
#                betas[beta_i] = self.betas[beta_i]
#
#        return numpy.sum(bx[self.best_set] * betas)
#            
#    def used_attributes(self, term=None):
#        """ Return a list of used attributes. If term (index) is given
#        return only attributes used in that single term.
#        
#        """
#        if term is None:
#            terms = numpy.where(self.best_set)[0]
#        else:
#            terms = [term]
#        attrs = set()
#        for ti in terms:
#            attri = numpy.where(self.dirs[ti] != 0.0)[0]
#            attrs.update([self.domain.attributes[i] for i in attri])
#        return attrs
#        
#    def evimp(self, used_only=True):
#        """ Return the estimated variable importance.
#        """
#        return evimp(self, used_only)
#        
#    def __reduce__(self):
#        return (EarthClassifier, (self._base_classifier, self.examples,
#                                  self.best_set, self.dirs, self.cuts,
#                                  self.betas, self.subsets,
#                                  self.rss_per_subset, self.gcv_per_subset),
#                {})
                                 
