import os
from os import path
import argparse

Configs = {
    'SOCKS_PROXY_PORT': 10808,
    'HTTP_PROXY_PORT': 10809,
    'HTTPS_PROXY_PORT': 10809,
}


def getSSHClientIP():
    '''
        Get the client IP according to SSH connection.
    '''
    sshConn = os.popen('echo $SSH_CONNECTION').read().strip()
    # We get a TCP quadruple: <SrcIP> <SrcPort> <DstIp> <DstPort>
    return sshConn.split(' ')[0]


class Proxifier(object):
    def proxy(self):
        pass

    def clear(self):
        pass

    def init(self):
        pass


class ProxyBash(Proxifier):
    def __init__(self) -> None:
        super().__init__()

        self.StartLine = '##### [START] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
        self.EndLine = '##### [END] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
        self.BashrcPath = path.expanduser('~/.bashrc')

    def _modifyBashrc(self, lines):
        with open(self.BashrcPath, 'r') as fp:
            bashrc = fp.read()

        bashrc = bashrc.split('\n')  # we wont consider replace \r\n to \n since it is linux
        for i in range(len(bashrc)):
            if bashrc[i].strip() == self.StartLine and bashrc[i + len(lines) + 1].strip() == self.EndLine:
                for j in range(len(lines)):
                    bashrc[i + j + 1] = lines[j]
                break

        with open(self.BashrcPath, 'w') as fp:
            fp.write('\n'.join(bashrc))

    def proxy(self, ip: str, httpPort: int, httpsPort: int):
        '''
            Proxy HTTP and HTTPs by modifying .bashrc to set `http_proxy` and `https_proxy` env variables.
            We are not going to use socks here currently, since `wget` and many other tools do not support
            socks proxy now.
        '''
        httpLine = 'export http_proxy=http://{}:{}'.format(ip, httpPort)
        httpsLine = 'export https_proxy=https://{}:{}'.format(ip, httpsPort)

        self._modifyBashrc(httpLine, httpsLine)

        print('[ProxyBash.proxy] Please run `source ~/.bashrc` manually or form a new connection.')

    def init(self):
        pass

    def clear(self):
        '''
            Invert of ProxyBash.proxy.
        '''
        self._modifyBashrc('#', '#')

        print('[ProxyBash.clear] Please run `source ~/.bashrc` manually or form a new connection.')


class ProxyGitHTTP(Proxifier):
    def __init__(self) -> None:
        super().__init__()

    def proxy(self, ip: str, httpPort: int, httpsPort: int):
        '''
            Proxy Git repository connection if you are using `git clone` and `git remote` with HTTP.
        '''
        os.system('git config --global http.proxy "http://{}:{}"'.format(ip, httpPort))
        os.system('git config --global https.proxy "https://{}:{}"'.format(ip, httpsPort))
        print('[proxyGitHTTP] Set.')

    def clear(self):
        '''
            Invert of ProxyGitHTTP.proxy.
        '''
        os.system('git config --global --unset http.proxy')
        os.system('git config --global --unset https.proxy')

        print('[clearProxyGitHTTP] Unset.')


class ProxyGitHubSSH(Proxifier):
    def __init__(self) -> None:
        super().__init__()
        assert Configs['SOCKS_PROXY_PORT'] >= 1, 'Socks port is required for `ProxyGitHubSSH`.'

    def _modifySSHConfig(self, lines):
        pass

    def proxy(self, ip: str, socksPort: int):
        StartLine = '##### [START] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
        EndLine = '##### [END] https://github.com/z0gSh1u/ProxyToSSHClient [DO NOT MODIFY] #####'
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
