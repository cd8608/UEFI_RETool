import idc
import idaapi
import idautils
import ida_kernwin
from idaapi import Choose2

from analyser import Analyser

class chooser_handler_t(idaapi.action_handler_t):
    def __init__(self, thing):
        idaapi.action_handler_t.__init__(self)
        self.thing = thing

    def activate(self, ctx):
        pass

    def update(self, ctx):
        if idaapi.is_chooser_tform(ctx.form_type):
            return idaapi.AST_ENABLE_FOR_FORM
        return idaapi.AST_DISABLE_FOR_FORM

class ProtsWindow(Choose2):
    """
    class to display protocols information output window
    """
    def __init__(self, title, analyser, nb=5):
        sizes = self._get_sizes(analyser)
        Choose2.__init__(
            self,
            title,
            [
                ["Address", sizes["Address"]],
                ["Name", sizes["Name"]],
                ["Service", sizes["Service"]],
                ["Place", sizes["Place"]],
                ["GUID", sizes["GUID"]],
            ],
            flags = 0,
            width = None,
            height = None,
            embedded = False
        )
        self.n = 0
        self.items = self._get_lines(analyser)
        self.selcount = 0
        self.modal = False
        self.popup_names = []

    def _get_sizes(self, analyser):
        """
        get maximum field sizes
        """
        sizes = {
            "Address": 0,
            "Name": 0,
            "Service": 0,
            "Place": 0,
            "GUID": 0
        }
        for prot in analyser.Protocols["All"]:
            if len("{addr:#x}".format(addr=prot["address"])) > sizes["Address"]:
                sizes["Address"] = len("{addr:#x}".format(addr=prot["address"]))
            if len(prot["protocol_name"]) > sizes["Name"]:
                sizes["Name"] = len(prot["protocol_name"])
            if len(prot["service"]) > sizes["Service"]:
                sizes["Service"] = len(prot["service"])
            if len(prot["protocol_place"]) > sizes["Place"]:
                sizes["Place"] = len(prot["protocol_place"])
            if len(self._get_guid(prot["guid"])) > sizes["GUID"]:
                sizes["GUID"] = len(self._get_guid(prot["guid"]))
        return sizes

    def _get_guid(self, guid_struct):
        """
        get GUID string
        """
        guid = str(map(hex, guid_struct))
        guid = guid.replace(", ", "-")
        guid = guid.replace("L", "")
        guid = guid.replace("'", "")
        return guid

    def _get_lines(self, analyser):
        """
        to fill line in the table
        """
        lines = []
        for prot in analyser.Protocols["All"]:
            lines.append([
                "{addr:#x}".format(addr=prot["address"]),
                prot["protocol_name"],
                prot["service"],
                prot["protocol_place"],
                self._get_guid(prot["guid"])
            ])
        return lines

    def _make_item(self):
        """
        make custom element
        """
        item = [
            idaapi.askstr(0, "", "Address"),
            idaapi.askstr(0, "", "Name"),
            idaapi.askstr(0, "", "Service"),
            idaapi.askstr(0, "", "Place"),
            idaapi.askstr(0, "", "GUID")
        ]
        self.n += 1
        return item

    def OnClose(self):
        print("[info] protocols window was closed")

    def OnEditLine(self, n):
        return n

    def OnInsertLine(self):
        self.items.append(self._make_item())
        print("[info] element was insert")

    def OnSelectLine(self, n):
        self.selcount += 1
        ea = int(self.items[n][0], 16)
        idc.jumpto(ea)
        print("[info] jump to {addr:#x}".format(addr=ea))
        return n

    def OnGetLine(self, n):
        return self.items[n]

    def OnGetSize(self):
        n = len(self.items)
        return n

    def OnDeleteLine(self, n):
        del self.items[n]
        print("[info] element was deleted")
        return n

    def OnRefresh(self, n):
        return n

    def OnGetLineAttr(self, n):
        return n

    def show(self):
        return self.Show(self.modal) >= 0

def run():
    analyser = Analyser()
    if analyser.valid:
        analyser.print_all()
        analyser.analyse_all()
        if len(analyser.Protocols["All"]):
            wind = ProtsWindow("Protocols", analyser, nb=10)
            wind.show()

if __name__=="__main__":
    run()