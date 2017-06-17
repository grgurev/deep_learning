import numpy as np

class Ensamble:
    def __init__(self):
        self.nets = list()

    def sample(self, x):
        '''
        Samples parameters from different distributions
        :param x:
        :return:
        '''
        if isinstance(x, dict):
            if len(x.keys()) == 1:
                key = list(x.keys())[0]
                low, high = x[key][:2]

                # uniform distribution
                if key == 'lin':
                    retval = np.random.uniform(low, high)

                # e.g. used for 0.001,..., 1000 ranges
                elif key == 'log':
                    retval = np.exp(np.random.uniform(*np.log((low, high))))

                # e.g. used for 0.9,..., 0.999 ranges
                elif key == 'inv-log':
                    retval = 1.0 - np.exp(np.random.uniform(*np.log([1.0 - high, 1.0 - low])))

                # round to integer if needed
                if isinstance(low, int) and isinstance(high, int):
                    retval = round(retval)
                elif len(x[key]) is 3:
                    precision = x[key][2]
                    retval = round(retval, precision)
                return retval

            # recursively process dictionaries, lists and tupples
            return {key: self.sample(x[key]) for key in x.keys()}
        elif isinstance(x, list):
            return [self.sample(a) for a in x]
        elif isinstance(x, tuple):
            return (self.sample(a) for a in x)

        # sample boolean values
        elif x == 'bool':
            return (np.random.uniform() > 0.5)

        # do nothing by default
        return x

    def _create_net(self, net_dict):
        net_cls = net_dict['net_cls']
        arch = net_dict['arch']
        learning_dict = net_dict['learning_dict']

        # create net
        net = net_cls()
        net.create_net(arch, **learning_dict)

        return net

    def _sample_net_dict(self, net_cls, arch, data, learning_dict):
        sampled_arch = self.sample(arch)
        sampled_learning_dict = self.sample(learning_dict)

        net_dict = {'net_cls': net_cls,
                    'arch': sampled_arch,
                    'data': data,
                    'learning_dict': sampled_learning_dict,
                    'global_step': 0,
                    'stats': None}

        net = self._create_net(net_dict)
        net_dict['name'] = net.name_extension()

        return net_dict, net

    def add_nets(self, net_cls, arch, data, learning_dict, no_of_nets):
        net = net_cls()
        for _ in range(no_of_nets):
            # create net and summary writer (check parameters if nothing else)
            net_dict, _ = self._sample_net_dict(net_cls, arch, data, learning_dict)
            self.nets.append(net_dict)
            print(net_dict['name'])

    def train_all(self, train_dict):
        for net_dict in self.nets:
            print('#'*80)
            net = self._create_net(net_dict)
#            train_dict['data'] = net_dict['data']
            global_step, stats = net.train(**train_dict, data=net_dict['data'])
            print(stats)
            net_dict['global_step'] = global_step
            net_dict['stats'] = stats