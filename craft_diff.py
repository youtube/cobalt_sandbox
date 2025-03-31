import argparse
import subprocess
import yaml
import os
import logging
import sys

class Crafter(object):
    def __init__(self, git_dir, our_branch, our_branch_edit, upstream_branch, upstream_branch_edit):
        self.git_dir = git_dir
        self.our_branch = our_branch
        self.our_branch_edit = our_branch_edit
        self.upstream_branch = upstream_branch
        self.upstream_branch_edit = upstream_branch_edit

    def run_git_cmd(self, cmd, ignore_output=False):
        full_cmd = ["git" ]  + cmd
        logging.info("Running %s", ' '.join(full_cmd))
        if ignore_output:
            subprocess.run(full_cmd, cwd=self.git_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(full_cmd, cwd=self.git_dir)
        
    def create_our_diff_branch(self, deletedirs, push):
        # Force delete whatever was there first
        self.run_git_cmd(["branch","-D", self.our_branch_edit])
        # Create it from ours
        self.run_git_cmd(["checkout","-b",self.our_branch_edit, self.our_branch])
        for dir in deletedirs:
            self.run_git_cmd(["rm","-rf",dir])
        self.run_git_cmd(["commit","-m","delete dirs","--no-verify"])
        if push:
            self.run_git_cmd(["push","sandbox","-f"])

    def create_upstream_diff_branch(self, deletedirs, push):
        # Force delete whatever was there first
        self.run_git_cmd(["branch","-D", self.upstream_branch_edit])
        # Create it from upstream
        self.run_git_cmd(["checkout","-b", self.upstream_branch_edit, self.upstream_branch])
        for dir in deletedirs:
            self.run_git_cmd(["rm","-rf",dir])
        self.run_git_cmd(["commit","-m","delete dirs", "--no-verify"])
        if push:
            self.run_git_cmd(["push","sandbox","-f"])

def main():
    logging.basicConfig(stream=sys.stdout,level=logging.DEBUG)
    argparser = argparse.ArgumentParser()
    argparser.add_argument("spec", nargs='?', default="dirs.yaml", help="Path to the dirs.yaml file")
    argparser.add_argument("--our_branch", default="main")
    argparser.add_argument("--upstream_branch",default="chromium/m114")
    argparser.add_argument("--git_dir",default="src")
    argparser.add_argument("--our_branch_edit", default="diff_edit")
    argparser.add_argument("--upstream_branch_edit", default="chromium_m114_diff")
    argparser.add_argument("--push", action="store_true", default=False)
    args = argparser.parse_args()

    spec_path = args.spec
    if not os.path.exists(spec_path):
        print(f"Error: File '{spec_path}' not found.")
        return

    try:
        with open(spec_path, 'r') as f:
            data = yaml.safe_load(f)
        print(f"Successfully loaded {spec_path}")
        print("{!r}".format(data))
        dirs_to_delete_in_ours = data['ours'] + \
                            data['our_files'] + \
                            data['our_owned_dep'] + \
                            data['our_added_dep'] + \
                            data['updated']
        dirs_to_delete_in_upstream = data['our_deleted_dep'] + data['updated']
        
        crafter = Crafter(args.git_dir, 
                        args.our_branch, 
                        args.our_branch_edit, 
                        args.upstream_branch, 
                        args.upstream_branch_edit
                        )
        crafter.create_our_diff_branch(dirs_to_delete_in_ours, args.push)
        crafter.create_upstream_diff_branch(dirs_to_delete_in_upstream, args.push)

    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format in '{spec_path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
