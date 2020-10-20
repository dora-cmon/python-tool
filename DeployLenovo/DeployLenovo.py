
'''
Date         : 2020-09-16 20:15:27
LastEditors  : LiZhenglin
LastEditTime : 2020-10-20 21:03:17
FilePath     : /python-tools/DeployLenovo.py/DeployLenovo.py
'''

from time import time, sleep
from SSHConnectRunCommand.Tools import *
from SSHConnectRunCommand.ShellHandler import ShellHandler


class DeployLenovo(ShellHandler):

    def checkLock(self):
        lock_flag = True
        stdin, stdout, stderr = self.executeCmd(
            'stat -c %Y deploy.lock')
        if stdout == []:
            lock_flag = False
        else:
            lock_file_create_time_str = list2string(stdout)
            if lock_file_create_time_str.startswith('1600'):
                lock_file_create_time = int(lock_file_create_time_str[0:10])
            else:
                lock_file_create_time = int(time())

            if lock_file_create_time < int(time()) - 3*60:
                self.removeLock()
                lock_flag = False

        if lock_flag:
            print("Someone is deploying, please wait for 3 minutes.")

        return lock_flag

    def createLock(self):
        self.executeCmd('touch /root/deploy.lock')
        self.execCmdGetExpect('ls /root', 'deploy.lock', 'Create lock file')

    def removeLock(self):
        self.executeCmd('rm /root/deploy.lock')
        self.execCmdGetexpectNot('ls /root', 'deploy.lock', 'Remove lock file')

    def checkVersion(self):
        version = '1.0'
        _, stdout, _ = self.executeCmd('cat /root/pythonScriptVersion')
        if not findInStrList(version, stdout):
            print("Not the latest version, please use the latest one!")
            exitWithPress()

    def execCmdGetExpect(self, cmd, expect, out):
        print('%s ing, DO NOT CLOSE WINDOW!!!' % out)
        stdin, stdout, stderr = self.executeCmd(cmd)

        success_flag = False
        if type(expect) is list:
            if expect == stdout:    # []
                success_flag = True
            else:
                for e in expect:
                    if e == [] and stdout == []:
                        success_flag = True
                    elif e != [] and findInStrList(e, stdout):
                        success_flag = True
        else:
            if findInStrList(expect, stdout):
                success_flag = True

        if success_flag:
            print('%s SUCCESS!' % out)
        else:
            print('%s FAILED, please retry, if failed in several times, contact LiZhenglin or LiHuan to Deploy manually!' % out)
            self.removeLock()
            exitWithPress()

    def execCmdGetexpectNot(self, cmd, expect_not, out):
        print('%s ing, DO NOT CLOSE WINDOW!!!' % out)
        stdin, stdout, stderr = self.executeCmd(cmd)

        appear_flag = False
        if type(expect_not) is list:
            if expect_not == stdout:    # []
                appear_flag = True
            else:
                for e in expect_not:
                    if findInStrList(e, stdout):
                        appear_flag = True
        else:
            if findInStrList(expect_not, stdout):
                appear_flag = True

        if not appear_flag:
            print('%s SUCCESS!' % out)
        else:
            print('%s FAILED, please retry, if failed in several times, contact LiZhenglin or LiHuan to Deploy manually!' % out)
            self.removeLock()
            exitWithPress()

    def checkDeploySuccess(self):
        success_flag = False
        _, stdout1, _ = self.executeCmd(
            'cat /root/LenovoBackDemo/target/nohup.out')
        if findInStrList('Started DemoApplication in', stdout1):
            print('Deploy Success!')
            success_flag = True
        else:
            sleep(15)
            _, stdout2, _ = self.executeCmd(
                'cat /root/LenovoBackDemo/target/nohup.out')
            if list2string(stdout1) == list2string(stdout2):
                print(
                    'Deploy failed, please retry!')
                self.removeLock()
                exitWithPress()
        return success_flag

    def deploy(self):
        # find project folder
        self.execCmdGetExpect('cd /root && ls', 'LenovoBackDemo',
                              "Find folder LenovoBackDemo")
        # enter project folder
        self.executeCmd('cd /root/LenovoBackDemo')
        self.execCmdGetExpect('ls', 'src', "Enter folder LenovoBackDemo")
        # checkout to master & pull
        self.execCmdGetExpect('git checkout master && git pull && git pull',
                              "Already up to date.", "Checkout to master and pull")
        # build project
        self.execCmdGetExpect('mvn clean package',
                              'BUILD SUCCESS', 'Build project')
        # kill java process
        self.executeCmd("""ps -aux | grep "java -Dfile.encoding=utf-8 -jar lenovo-back-1.0.0-SNAPSHOT.jar" | grep Sl | awk '{print $2}' | xargs kill""")
        sleep(3)
        self.execCmdGetExpect('pgrep java', [[], 'For more details see kill(1).'], "Kill java process")
        # enter folder target
        self.executeCmd('cd target')
        self.execCmdGetExpect(
            'ls', 'lenovo-back-1.0.0-SNAPSHOT.jar', 'Enter folder target')
        # run java process
        self.executeCmd('rm nohup.out')
        print("Deploy ing, Do not close ")
        self.executeCmd(
            'nohup java -Dfile.encoding=utf-8 -jar lenovo-back-1.0.0-SNAPSHOT.jar &')

    def interact(self):
        self.checkVersion()
        while(self.checkLock()):
            sleep(5)
        self.createLock()
        self.deploy()
        while(not self.checkDeploySuccess()):
            sleep(3)
        self.removeLock()


if __name__ == '__main__':
    host_addr = "123.57.64.186"
    user_name = "root"
    password = ""
    deploy_lenovo = DeployLenovo(host_addr, user_name, password)
    deploy_lenovo.interact()
    exitWithPress()
