from __future__ import print_function
from nose.tools import *
from uberdoc.udoc import Uberdoc, Config
import os
import shutil


# problem: each method in uberdoc assumes everything happens in current
# working dir? how do I run tests in a dir which is not current wd?
# there should be a central way to tell uberdoc which dir is the doc
# dir, shouldnt have to be only the working dir!

class TestUberdoc:
    BUILD_DIR = "testbuild"
    TEST_CONF_FILE = "tests/uberdoc_tests.cfg"

    def setup(self):
        self.conf = Config(self.TEST_CONF_FILE)
        self.conf['doc_dir'] = 'testbuild'
        self.u = Uberdoc(self.conf)
        self.clean()
        self.out_dir = os.path.join(self.BUILD_DIR, self.conf["out_dir"])

    @with_setup(setup)    
    def test_env(self):
        self.u.init_doc()
        self.u.check_env()

    @with_setup(setup)
    def test_init_doc(self):
        self.u.init_doc()
        in_dir = os.path.join(self.BUILD_DIR, self.conf["in_dir"])
        assert_true(os.path.isdir(in_dir))
        assert_true(os.path.isdir(os.path.join(in_dir, "chapter1")))
        assert_true(os.path.isdir(os.path.join(in_dir, "chapter2")))
        assert_true(os.path.isfile(os.path.join(self.BUILD_DIR, "uberdoc.cfg")))

    @with_setup(setup)
    def test_clean(self):   
        os.mkdir(self.out_dir)
        assert_true(os.path.isdir(self.out_dir))
        self.u.clean(recreate_out = False)
        assert_false(os.path.isdir(self.out_dir))
        self.u.clean(recreate_out = True)
        assert_true(os.path.isdir(self.out_dir))

    @with_setup(setup)
    def test_read_toc(self):
        self.u.init_doc()
        lines = self.u.read_toc()
        assert_true(len(lines) == 2)
        assert_equals(lines[0], "chapter1")
        assert_equals(lines[1], "chapter2")

    @with_setup(setup)  
    def test_version_with_git(self):
        self.u.init_doc()
        self.u.git()
        assert_true(os.path.isfile(os.path.join(self.BUILD_DIR, ".gitignore")))
        version = self.u.version()
        
        abs_doc_dir = os.path.abspath(self.conf["doc_dir"])
        
        env = [("GIT_WORK_TREE", abs_doc_dir), ("GIT_DIR", os.path.join(abs_doc_dir, ".git"))]
        returncode, version_str, error = self.u.cmd('git log -1 --format="%h" --date=short', 
            cwd = abs_doc_dir,
            env = env) 
        #version_str = version_str.decode('utf-8')
        version_str = version_str.rstrip()
        #version = str(version.decode('utf-8'))
        print(version)
        print(version_str)
        assert_true(version.endswith("(" + version_str + ")"))

    @with_setup(setup)  
    def test_build_html(self):
        self.u.init_doc()
        self.u.build()
        out_file = os.path.join(self.BUILD_DIR, self.conf["out_dir"], self.conf["doc_filename"])
        assert_true(os.path.isfile(out_file + ".html"))

    @with_setup(setup)  
    def test_build_pdf(self):
        self.u.init_doc()
        self.u.build(pdf = True)
        out_file = os.path.join(self.BUILD_DIR, self.conf["out_dir"], self.conf["doc_filename"])
        assert_true(os.path.isfile(out_file + ".pdf"))

    @with_setup(setup)  
    def test_conf(self):
        conf = Config(self.TEST_CONF_FILE)
        assert_equals(conf["in_dir"], "in")

        #u = Uberdoc2()
        #u.generate_file_list()



    def clean(self):
        if os.path.isdir(self.BUILD_DIR):
            shutil.rmtree(self.BUILD_DIR)
        os.mkdir(self.BUILD_DIR)