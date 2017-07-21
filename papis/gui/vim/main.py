import os
import re
import textwrap
import subprocess
import tempfile
import logging
import papis.config
import papis.commands.external


main_vim_path = os.path.join(
    os.path.dirname(__file__),
    "main.vim"
)

pick_vim_path = os.path.join(
    os.path.dirname(__file__),
    "pick.vim"
)


def pick(
        options,
        header_filter=lambda x: x,
        body_filter=None,
        match_filter=lambda x: x
        ):
    temp_file = tempfile.mktemp()
    fd = open(temp_file, "w+")
    fd.write("# Put your cursor on a line and press enter to pick\n")
    headers = [
        header_filter(d) for d in
        options
    ]
    for header in headers:
        fd.write(header+"\n")
    fd.close()
    process = subprocess.call(
        ["vim", "-S", pick_vim_path, temp_file]
    )
    fd = open(temp_file)
    index = fd.read()
    fd.close()
    ret = options[int(index)-2]
    print(ret)
    return ret


class Gui(object):


    def __init__(self):
        self.documents = []
        self.logger = logging.getLogger("gui:vim")
        self.main_vim_path = main_vim_path


    def export_variables(self, args):
        """Export variables so that vim can use some papis information
        """
        external_cmd = papis.commands.external.External()
        external_cmd.set_args(args)
        external_cmd.export_variables()

    def main(self, documents, args):
        header_format = papis.config.get(
            "vim-header-format",
            default=textwrap.dedent("""\
            Title : {doc[title]}
            Author: {doc[author]}
            Year  : {doc[year]}
            -------
            """)
        )
        self.export_variables(args)
        temp_file = tempfile.mktemp()
        self.logger.debug("Temp file = %s" % temp_file)
        fd = open(temp_file, "w+")
        for doc in documents:
            fd.write(
                header_format.format(doc=doc)
            )
        fd.close()

        subprocess.call(
                ["vim", "-S", self.main_vim_path, temp_file]
        )
