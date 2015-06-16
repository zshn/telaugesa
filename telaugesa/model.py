"""Models

This module documented some training models

+ Feedforward Neural Network (including ConvNets)
"""

from telaugesa.optimize import corrupt_input;

class FeedForward(object):
    """Feedforward Neural Network model"""
    
    def __init__(self,
                 layers=None):
        """Initialize feedforward model
        
        Parameters
        ----------
        in_dim : int
            number of input size
        layers : list
            list of layers
        """
        self.layers=layers;
        
    def fprop(self,
              X):
        """Forward propagation
        
        Parameters
        ----------
        X : matrix or 4D tensor
            input samples, the size is (number of cases, in_dim)
            
        Returns
        -------
        out : list
            output list from each layer
        """
        
        out=[];
        level_out=X;
        for k, layer in enumerate(self.layers):
            
            level_out=layer.apply(level_out);
            
            out.append(level_out);
            
        return out;
    
    @property
    def params(self):
        return [param for layer in self.layers if hasattr(layer, 'params') for param in layer.params];
    
class AutoEncoder(object):
    """AutoEncoder model for MLP layers
    
    This model only checking the condition of auto-encoders,
    the training is done by FeedForward model
    """
    
    def __init__(self, layers=None):
        """Initialize AutoEncoder
        
        Parameters
        ----------
        layers : tuple
            list of MLP layers
        """
        
        self.layers=layers;
        self.check();
        
    def check(self):
        """Check the validity of an AutoEncoder
        """
        
        assert self.layers[0].in_dim==self.layers[-1].out_dim, \
            "Input dimension is not match to output dimension";
           
        for layer in self.layers:
            assert hasattr(layer, 'params'), \
                "Layer doesn't have necessary parameters";
                
    def fprop(self,
              X,
              corruption_level=0.,
              epoch=None,
              decay_rate=1.):
        """Forward pass of auto-encoder
        
        Parameters
        ----------
        X : matrix
            number of samples in (number of samples, dim of sample)
        corruption_level : float
            corruption_level on data
        
        Returns
        -------
        out : matrix
            output list for each layer
        """
        
        out=[];
        
        if epoch is not None:
            self.corruption_level=corruption_level*(epoch**(-decay_rate));
        else:
            self.corruption_level=corruption_level;
        
        if self.corruption_level == 0.:
            level_out=X;
        else:
            level_out=corrupt_input(X, self.corruption_level);
        for k, layer in enumerate(self.layers):
            
            level_out=layer.apply(level_out);
            
            out.append(level_out);
            
        return out;
    
    @property
    def params(self):
        return [param for layer in self.layers if hasattr(layer, 'params') for param in layer.params];
                
class ConvKMeans(object):
    """Convolutional K-means"""
    
    def __init__(self, layers):
        """Init a Conv K-means model
        
        Parameters
        ----------
        layers : tuple of size 2
            one conv layer, one arg-max pooling layer
        """
        
        assert len(layers)==2, \
            "Too many layers for Conv K-means";
        
        self.layers=layers;
        
    def get_layer(self):
        """Get trained convolution layer
        """
        return self.layers[0];
    
    def fprop(self, X):
        """Get activation map
        
        Parameters
        ----------
        X : matrix or 4D tensor
            input samples, the size is (number of cases, in_dim)
            
        Returns
        -------
        out : list
            output list from each layer
        """
        
        out=[];
        level_out=X;
        for k, layer in enumerate(self.layers):
            level_out=layer.apply(level_out);
            out.append(level_out);
            
        return out;
        