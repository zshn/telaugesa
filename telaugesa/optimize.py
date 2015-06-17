"""Optimization method

Supported method:

+ Stochastic gradient descent
"""

from collections import OrderedDict;

import numpy as np;

import theano;
import theano.tensor as T;

def sgd(cost,
        params,
        updates=None,
        learning_rate=0.1):
    """Stochastic Gradient Descent (SGD)
    
    Parameters
    ----------
    cost : scalar
        total cost of the cost function.
    params : list
        parameter list
    learning_rate : float
        learning rate of SGD
        
    Returns
    -------
    updates : OrderedDict
        dictionary of updates
    """
    
    if updates is None:
        updates=OrderedDict();
    
    gparams=T.grad(cost, params);
    
    for param, gparam in zip(params, gparams):
        updates[param] = param - learning_rate * gparam;
        
    return updates;

def apply_momentum(updates,
                   params,
                   momentum=0.):
    """Apply momentum to update updates dictionary
    
    Parameters
    ----------
    updates : OrderedDict
        list of parameter updates
    params : list
        list of params to be updated
    momentum : float
        The amount of momentum to apply
    
    Returns
    -------
    updates : OrderedDict
        updated list of parameters
    """
    
    updates=OrderedDict(updates);
        
    for param in params:
        value = param.get_value(borrow=True);
        velocity=theano.shared(np.zeros(value.shape, dtype=value.dtype),
                               broadcastable=param.broadcastable);
        x=momentum*velocity+updates[param]
        updates[velocity]=x-param;
        updates[param]=x;
    
    return updates;

def apply_nestrov_momentum(updates,
                           params,
                           momentum=None):
    """Apply Nestrov momentum to update updates dictionary
    
    Parameters
    ----------
    updates : OrderedDict
        list of parameter updates
    params : list
        list of params to be updated
    momentum : float
        The amount of momentum to apply
    
    Returns
    -------
    updates : OrderedDict
        updated list of parameters
    """
    
    updates=OrderedDict(updates);
        
    for param in params:
        value = param.get_value(borrow=True);
        velocity=theano.shared(np.zeros(value.shape, dtype=value.dtype),
                               broadcastable=param.broadcastable);
        x=momentum*velocity+updates[param]-param;
        updates[velocity]=x;
        updates[param]=momentum*x+updates[param];
    
    return updates;

def adagrad(cost,
            params,
            updates=None,
            learning_rate=0.1,
            eps=1e-6):
    """Adagrad
    
    Parameters
    ----------
    cost : scalar
        total cost of the cost function.
    params : list
        parameter list
    learning_rate : float
        learning rate of SGD
    eps : float
        Small value added for numerical stability
        
    Returns
    -------
    updates : OrderedDict
        list of updated parameters
    """
    
    if updates is None:
        updates=OrderedDict();
        
    gparams=T.grad(cost, params);
    
    for param, gparam in zip(params, gparams):
        value=param.get_value(borrow=True);
        accu=theano.shared(np.zeros(value.shape, dtype=value.dtype),
                           broadcastable=param.broadcastable);
                           
        accu_new=accu+gparam**2;
        updates[accu]=accu_new;
        updates[param]=param-(learning_rate*gparam/T.sqrt(accu_new+eps));
        
    return updates;

def adadelta(cost,
             params,
             updates=None,
             learning_rate=0.1,
             eps=1e-6,
             rho=0.95):
    """Adadelta
    
    Parameters
    ----------
    cost : scalar
        total cost of the cost function.
    params : list
        parameter list
    learning_rate : float
        learning rate of SGD
    eps : float
        Small value added for numerical stability
    rho : float
        Squared gradient moving average decay factor
        
    Returns
    -------
    updates : OrderedDict
        list of updated parameters
    """
    
    if updates is None:
        updates=OrderedDict();
        
    gparams=T.grad(cost, params);
    
    for param, gparam in zip(params, gparams):
        value=param.get_value(borrow=True);
        accu=theano.shared(np.zeros(value.shape, dtype=value.dtype),
                           broadcastable=param.broadcastable);
                           
        delta_accu=theano.shared(np.zeros(value.shape, dtype=value.dtype),
                                 broadcastable=param.broadcastable);
                           
        accu_new=rho*accu+(1-rho)*gparam**2;
        updates[accu]=accu_new;
        
        update=(gparam*T.sqrt(delta_accu+eps)/T.sqrt(accu_new+eps));
        updates[param]=param-learning_rate*update;
        
        delta_accu_new=rho*delta_accu+(1-rho)*update**2;
        updates[delta_accu]=delta_accu_new;
        
    return updates;

def gd_updates(cost,
               params,
               updates=None,
               momentum=None,
               nesterov=False,
               max_norm=5.0,
               learning_rate=0.1,
               eps=1e-6,
               rho=0.95,
               method="sgd"):
    """Gradient Descent based optimization
    
    Note: should be a class to make flexible call
    
    Parameters
    ----------
    cost : scalar
        total cost of the cost function.
    params : list
        parameter list
    method : string
        optimization method: "sgd", "adagrad", "adadelta"
        
    Returns
    -------
    updates : OrderedDict
        dictionary of updates
    """
    
    if method=="adagrad":
        updates=adagrad(cost, params, updates, learning_rate=learning_rate, eps=eps);
    elif method=="adadelta":
        updates=adadelta(cost, params, updates, learning_rate=learning_rate, eps=eps, rho=rho);
    elif method=="sgd":
        updates=sgd(cost, params, updates, learning_rate=learning_rate);
        
        if momentum is not None:
            if nesterov==True:
                updates=apply_nestrov_momentum(updates, params, momentum=momentum);
            else:
                updates=apply_momentum(updates, params, momentum=momentum);
            
    return updates;

theano_rng=T.shared_randomstreams.RandomStreams(1234);

def dropout(shape, prob=0.):
    """generate dropout mask
    
    Parameters
    ----------
    shape : tuple
        shape of the dropout mask
    prob : double
        probability of each sample
        
    Returns
    -------
    mask : tensor
        dropout mask
    """
    
    mask=theano_rng.binomial(n=1, p=1-prob, size=shape);
    return T.cast(x=mask, dtype="float32");

def multi_dropout(shapes, prob=0.):
    """generate a list of dropout mask
    
    Parameters
    ----------
    shapes : tuple of tuples
        list of shapes of dropout masks
    prob : double
        probability of each sample
    
    Returns
    -------
    masks : tuple of tensors
        list of dropout masks
    """
    return [dropout(shape, dropout) for shape in shapes];

def apply_dropout(X, mask=None):
    """apply dropout operation
    
    Parameters
    ----------
    X : tensor
        data to be masked
    mask : dropout mask
    
    Returns
    -------
    masked_X : tensor
        dropout masked data
    """
    
    if mask is not None:
        return X*mask;
    else:
        return X;
    
def corrupt_input(X, corruption_level=0.):
    """Add noise on data
    
    Parameters
    ----------
    X : tensor
        data to be corrupted
    corruption_level : double
        probability of the corruption level
    Returns
    -------
    corrupted_out : tensor
        corrupted output 
    """
    
    return apply_dropout(X, dropout(X.shape, corruption_level));