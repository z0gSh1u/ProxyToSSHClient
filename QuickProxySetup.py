'''
    quick-proxy-setup

    by z0gSh1u @ https://github.com/z0gSh1u/quick-proxy-setup
'''

import os
import sys
from os import path
import json

## Utilities ##

PublicStartLine = '##### [START] https://github.com/z0gSh1u/quick-proxy-setup [DO NOT MODIFY] #####'
PublicEndLine = '##### [END] https://github.com/z0gSh1u/quick-proxy-setup [DO NOT MODIFY] #####'
ProxyIP = None
HTTPPort = None
SocksPort = None


def getSSHClientIP():
    '''
        Get the client IP according to SSH connection.
    '''
    # We get a TCP quadruple: <SrcIP> <SrcPort> <DstIp> <DstPort>
    sshConn = os.popen('echo $SSH_CONNECTION').read().strip()
    sshConn = sshConn.split(' ')
    assert len(sshConn) == 4
    return sshConn[0]


## Utilities ##

## Proxifiers ##


class Proxifier(object):
    def __init__(self) -> None:
        pass

    def init(self):
        pass

    def proxy(self):
        pass

    def clear(self):
        pass


class ProxyBash(Proxifier):
    '''
        Proxy HTTP and HTTPs by modifying .bashrc to set `http_proxy` and `https_proxy` env variables.

        We are not going to use socks here currently, since `wget` and many other tools do not support
        socks proxy now.
        
        With bash proxified, conda inherits.
    '''
    def __init__(self) -> None:
        super().__init__()

        self.StartLine = PublicStartLine
        self.EndLine = PublicEndLine
        self.ContentLength = 2
        self.BashrcPath = path.expanduser('~/.bashrc')

        self._updateBashrcReading()

    def _updateBashrcReading(self):
        with open(self.BashrcPath, 'r') as fp:
            self.Bashrc = fp.read()

        self.SplitBashrc = self.Bashrc.split('\n')  # we wont consider replace \r\n to \n since it is linux

    def _findStartLine(self):
        for i in range(len(self.SplitBashrc)):
            if self.SplitBashrc[i].strip() == self.StartLine:
                endLineIndex = i + self.ContentLength + 1
                if endLineIndex < len(self.SplitBashrc) and self.SplitBashrc[endLineIndex].strip() == self.EndLine:
                    return i
                else:
                    assert False, '[{}] StartLine found but EndLine is invalid. Please check ~/.bashrc manually.'.format(
                        str(self.__class__))
        return -1

    def _modifyBashrc(self, lines):
        # backup
        os.system('cp ~/.bashrc ~/.bashrc.ProxyToSSHClient.bak')
        print('~/.bashrc is backed up to ~/.bashrc.ProxyToSSHClient.bak')

        startLineNo = self._findStartLine()
        assert startLineNo != -1, 'Cannot find corresponding lines in ~/.bashrc, maybe you should call `init` first.'

        for j in range(len(lines)):
            self.SplitBashrc[startLineNo + j + 1] = lines[j]

        with open(self.BashrcPath, 'w') as fp:
            fp.write('\n'.join(self.SplitBashrc))

    def init(self):
        assert self._findStartLine() == -1, '[ProxyBash] ~/.bashrc has been initialized. Aborting the pipeline.'.format(
            str(self.__class__))

        self.Bashrc += '\n\n{}{}\n{}\n'.format(self.StartLine, '\n#' * self.ContentLength, self.EndLine)

        with open(self.BashrcPath, 'w') as fp:
            fp.write(self.Bashrc)

        self._updateBashrcReading()

        print('[ProxyBash.init] Done.')

    def proxy(self):
        # check args
        assert len(ProxyIP) > 0
        assert HTTPPort > 0

        httpLine = 'export http_proxy=http://{}:{}'.format(ProxyIP, HTTPPort)
        # Dont use https protocol for https_proxy, since the proxy's SSL certificate cannot be verified.
        httpsLine = 'export https_proxy=http://{}:{}'.format(ProxyIP, HTTPPort)

        self._modifyBashrc([httpLine, httpsLine])

        print('[ProxyBash.proxy] Done. Please run `source ~/.bashrc` or form a new connection.')

    def clear(self):
        self._modifyBashrc(['#' for _ in range(self.ContentLength)])

        print('[ProxyBash.clear] Done. Please run `source ~/.bashrc` or form a new connection.')


class ProxyGitHTTP(Proxifier):
    '''
        Proxy Git repository connection if you are using `git clone` and `git remote` with HTTP.
    '''
    def __init__(self) -> None:
        super().__init__()

    def init(self):
        # Do nothing.
        print('[ProxyGitHTTP.init] Done.')

    def proxy(self):
        # check args
        assert len(ProxyIP) > 0
        assert HTTPPort > 0

        os.system('git config --global http.proxy "http://{}:{}"'.format(ProxyIP, HTTPPort))
        # Both http:// and https:// works.
        os.system('git config --global https.proxy "http://{}:{}"'.format(ProxyIP, HTTPPort))

        print('[ProxyGitHTTP.proxy] Done.')

    def clear(self):
        os.system('git config --global --unset http.proxy')
        os.system('git config --global --unset https.proxy')

        print('[ProxyGitHTTP.clear] Done.')


class ProxyGitHubSSH(Proxifier):
    '''
        Proxy GitHub git services when using `ssh git@github.com:22`.
    '''
    def __init__(self) -> None:
        super().__init__()

        self.StartLine = PublicStartLine
        self.EndLine = PublicEndLine
        self.ContentLength = 4
        self.SSHConfigPath = os.path.expanduser('~/.ssh/config')

        # Sometimes, this file doesnt exist. Create it.
        if not os.path.exists(self.SSHConfigPath):
            os.system('touch {}'.format(self.SSHConfigPath))

        self._updateSSHConfigReading()

    def _updateSSHConfigReading(self):
        with open(self.SSHConfigPath, 'r') as fp:
            self.SSHConfig = fp.read()

        self.SplitSSHConfig = self.SSHConfig.split('\n')  # we wont consider replace \r\n to \n since it is linux

    def _findStartLine(self):
        for i in range(len(self.SplitSSHConfig)):
            if self.SplitSSHConfig[i].strip() == self.StartLine:
                endLineIndex = i + self.ContentLength + 1
                if endLineIndex < len(
                        self.SplitSSHConfig) and self.SplitSSHConfig[endLineIndex].strip() == self.EndLine:
                    return i
                else:
                    assert False, '[{}] StartLine found but EndLine is invalid. Please check ~/.ssh/config manually.'.format(
                        str(self.__class__))
        return -1

    def _modifySSHConfig(self, lines):
        # backup
        os.system('cp ~/.ssh/config ~/.ssh/config.ProxyToSSHClient.bak')
        print('~/.ssh/config is backed up to ~/.ssh/config.ProxyToSSHClient.bak')

        startLineNo = self._findStartLine()
        assert startLineNo != -1, 'Cannot find corresponding lines in ~/.ssh/config, maybe you should call `init` first.'

        for j in range(len(lines)):
            self.SplitSSHConfig[startLineNo + j + 1] = lines[j]

        with open(self.SSHConfigPath, 'w') as fp:
            fp.write('\n'.join(self.SplitSSHConfig))

    def init(self):
        assert self._findStartLine() == -1, '[{}] ~/.ssh/config has been initialized. Aborting the pipeline.'.format(
            str(self.__class__))

        self.SSHConfig += '\n\n{}{}\n{}\n'.format(self.StartLine, '\n#' * self.ContentLength, self.EndLine)

        with open(self.SSHConfigPath, 'w') as fp:
            fp.write(self.SSHConfig)

        self._updateSSHConfigReading()

        print('[ProxyGitHubSSH.init] Done.')

    def proxy(self):
        assert len(ProxyIP) > 0
        assert SocksPort > 0

        sshLines = [
            'Host github.com', 'HostName github.com', 'User git',
            'ProxyCommand nc -v -x {}:{} %h %p'.format(ProxyIP, SocksPort)
        ]

        self._modifySSHConfig(sshLines)

        print('[ProxyGitHubSSH.proxy] Done.')

    def clear(self):
        self._modifySSHConfig(['#' for _ in range(self.ContentLength)])

        print('[ProxyGitHubSSH.clear] Done.')


## Proxifiers ##

if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Usage: python ProxyToSSHClient.py <recipe.json>'

    print('[ProxyToSSHClient] Start.')

    # Initialize recipe.
    with open(sys.argv[1], 'r') as fp:
        recipe = json.load(fp)

    ProxyIP = recipe['Network']['IP'].replace('<SSHClient>', getSSHClientIP())
    HTTPPort = recipe['Network']['HTTPPort']
    SocksPort = recipe['Network']['SocksPort']

    # Print basis information.
    print('''
        [HTTP Proxy Server] {}:{}
        [Socks Proxy Server] {}:{}
    '''.format(ProxyIP, HTTPPort, ProxyIP, SocksPort))

    for handler in recipe['Pipeline']:
        print('[{}]'.format(handler))
        obj = eval('{}()'.format(handler))
        steps = recipe['Pipeline'][handler].replace(' ', '').strip().split(',')
        for step in steps:
            eval('obj.{}()'.format(step))
        print('------------------------------')

    print('[ProxyToSSHClient] Exit.')
