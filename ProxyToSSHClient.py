'''
    ProxyToSSHClient
    @ https://github.com/z0gSh1u/ProxyToSSHClient
'''

import os
from os import path
import yaml

Configs = {
    'SOCKS_PROXY_PORT': 10808,
    'HTTP_PROXY_PORT': 10809,
    'HTTPS_PROXY_PORT': 10809,
}


def getSSHClientIP():
    '''
        Get the client IP according to SSH connection.
    '''
    # We get a TCP quadruple: <SrcIP> <SrcPort> <DstIp> <DstPort>
    sshConn = os.popen('echo $SSH_CONNECTION').read().strip()
    return sshConn.split(' ')[0]


class Proxifier(object):
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
    '''
    def __init__(self) -> None:
        super().__init__()
        assert Configs['HTTP_PROXY_PORT'] >= 1, 'HTTP port is required for `ProxyBash`.'
        assert Configs['HTTPS_PROXY_PORT'] >= 1, 'HTTPS port is required for `ProxyBash`.'

        self.StartLine = '##### [START] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
        self.EndLine = '##### [END] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
        self.BashrcPath = path.expanduser('~/.bashrc')
        self.ContentLength = 2

        with open(self.BashrcPath, 'r') as fp:
            self.Bashrc = fp.read()

        self.SplitBashrc = self.Bashrc.split('\n')  # we wont consider replace \r\n to \n since it is linux

    def _findStartLine(self):
        for i in range(len(self.SplitBashrc)):
            if self.SplitBashrc[i].strip() == self.StartLine:
                if self.SplitBashrc[i + self.ContentLength + 1].strip() == self.EndLine:
                    return i
                else:
                    assert False, '[ProxyBash] StartLine found but EndLine is invalid. Please check ~/.bashrc manually.'
            return -1

    def _modifyBashrc(self, lines):
        startLineNo = self._findStartLine()
        assert startLineNo != -1, 'Cannot find corresponding lines in ~/.bashrc, maybe you should call `init` first.'

        for j in range(len(lines)):
            self.SplitBashrc[startLineNo + j + 1] = lines[j]

        with open(self.BashrcPath, 'w') as fp:
            fp.write('\n'.join(self.SplitBashrc))

    def init(self):
        with open(self.BashrcPath, 'r') as fp:
            bashrc = fp.read()

        bashrc += '\n{}\n#\n#\n{}'.format(self.StartLine, self.EndLine)

        with open(self.BashrcPath, 'w') as fp:
            fp.write('\n'.join(bashrc))

        print('[ProxyBash.init] Init done.')

    def proxy(self, ip: str, httpPort: int, httpsPort: int):
        httpLine = 'export http_proxy=http://{}:{}'.format(ip, httpPort)
        httpsLine = 'export https_proxy=https://{}:{}'.format(ip, httpsPort)

        self._modifyBashrc(httpLine, httpsLine)

        print('[ProxyBash.proxy] Please run `source ~/.bashrc` manually or form a new connection.')

    def clear(self):
        self._modifyBashrc('#', '#')

        print('[ProxyBash.clear] Please run `source ~/.bashrc` manually or form a new connection.')


class ProxyGitHTTP(Proxifier):
    '''
        Proxy Git repository connection if you are using `git clone` and `git remote` with HTTP.
    '''
    def __init__(self) -> None:
        super().__init__()
        assert Configs['HTTP_PROXY_PORT'] >= 1, 'HTTP port is required for `ProxyGitHTTP`.'
        assert Configs['HTTPS_PROXY_PORT'] >= 1, 'HTTPS port is required for `ProxyGitHTTP`.'

    def init(self):
        print('[ProxyGitHTTP.init] Init done.')

    def proxy(self, ip: str, httpPort: int, httpsPort: int):
        os.system('git config --global http.proxy "http://{}:{}"'.format(ip, httpPort))
        os.system('git config --global https.proxy "https://{}:{}"'.format(ip, httpsPort))
        print('[proxyGitHTTP.proxy] Set.')

    def clear(self):
        os.system('git config --global --unset http.proxy')
        os.system('git config --global --unset https.proxy')

        print('[ProxyGitHTTP.clear] Unset.')


class ProxyGitHubSSH(Proxifier):
    def __init__(self) -> None:
        super().__init__()
        assert Configs['SOCKS_PROXY_PORT'] >= 1, 'Socks port is required for `ProxyGitHubSSH`.'

        self.StartLine = '##### [START] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
        self.EndLine = '##### [END] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
        self.SSHConfigPath = os.path.expanduser('~/.ssh/config')

    def init(self):
        if os.path.exists(self.SSHConfigPath):
            with open(self.SSHConfigPath, 'r') as fp:
                sshConfig = fp.read()
        else:
            sshConfig = ''

        sshConfig += '\n{}\n#\n#\n{}'.format(self.StartLine, self.EndLine)

        with open(self.SSHConfigPath, 'w') as fp:
            fp.write('\n'.join(sshConfig))

        print('[ProxyGitHubSSH.init] Init done.')

    def _modifySSHConfig(self, lines):
        pass

    def proxy(self, ip: str, socksPort: int):
        BashrcPath = path.expanduser('~/.bashrc')
        sshLines = [
            'Host github.com', 'HostName github.com', 'User git',
            'ProxyCommand nc -v -x {}:{} %h %p'.format(ip, socksPort)
        ]


def proxyConda():
    pass


def clearProxyConda():
    pass


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # ProxyBash().proxy(getSSHClientIP(), Configs['HTTP_PROXY_PORT'], Configs['HTTPS_PROXY_PORT'])
    ProxyGitHubSSH().proxy(getSSHClientIP(), Configs['SOCKS_PROXY_PORT'])
