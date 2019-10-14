# -*- coding: utf-8 -*-

        #import pdb; pdb.set_trace()
from __future__ import unicode_literals, print_function

import sys
import os
import pyloco

# Push name collection to leaf nodes
# filter part of subnodes to stop the push
# distinguish definition from reference
#self._search_subnodes(node, ids, rtypes)

class PassSet(set):

    def __init__(self, iterable=None):
        self.elements = iterable

    def __or__(self, other):
        return other

    def __ior__(self, other):
        return other

    def __ror__(self, other):
        return other

    def __and__(self, other):
        return other if self.elements is None else other & set(self.elements)

    def __iand__(self, other):
        return other if self.elements is None else other & set(self.elements)

    def __rand__(self, other):
        return other if self.elements is None else other & set(self.elements)

name_resolvers = {
    "Program_Name": ["Program_Stmt"],
    "Object_Name": None,
    "Part_Name": None,
    "Scalar_Variable_Name": None,
    "Type_Name": ["Derived_Type_Stmt", "Use_Stmt"],
    "Procedure_Component_Name": None,
    "Procedure_Name": None,
    "Binding_Name": None,
    "Type_Param_Name": None,
    "Entry_Name": ["Entry_Stmt"],
    "Type_Param_Name_List": None,
    "Component_Name": None,
    "Interface_Name": None,
    "Arg_Name": None,
    "Procedure_Entity_Name": None,
    "Binding_Name_List": None,
    "Final_Subroutine_Name_List": None,
    "Final_Subroutine_Name": None,
    "Function_Name": ["Function_Subprogram", "Use_Stmt"],
    "Subroutine_Name": ["Subroutine_Subprogram", "Use_Stmt"],
    "Procedure_Name_List": None,
    "Object_Name_List": None,
    "Entity_Name": None,
    "Common_Block_Name": None,
    "Proc_Pointer_Name": None,
    "Variable_Name": None,
    "Array_Name": None,
    "External_Name_List": None,
    "External_Name": None,
    "Intrinsic_Procedure_Name_List": None,
    "Intrinsic_Procedure_Name": None,
    "Proc_Entity_Name": None,
    "Entity_Name_List": None,
    "Do_Construct_Name": ["Label_Do_Stmt", "Nonlabel_Do_Stmt"],
    "Index_Name": None,
    "Associate_Construct_Name": ["Associate_Stmt"],
    "Associate_Name": None,
    "Case_Construct_Name": None,
    "Forall_Construct_Name": ["Forall_Construct_Stmt"],
    "Where_Construct_Name": ["Where_Construct_Stmt"],
    "If_Construct_Name": ["If_Then_Stmt"],
    "Select_Construct_Name": ["Select_Type_Stmt"],
    "Block_Data_Name": None,
}


# NOTE: (resstmt, scope_stmt, forstmt)
 
res_all_stmts = {
    "Derived_Type_Stmt": (None, None),
    "Type_Param_Def_Stmt": ("Derived_Type_Def", None), # within Type Construct
    "Data_Component_Def_Stmt": ("Derived_Type_Def", None), # within Type Construct
    "Proc_Component_Def_Stmt": ("Derived_Type_Def", None), # within Type Construct
    "Specific_Binding": ("Derived_Type_Def", None), # within Type Construct
    "Generic_Binding": ("Derived_Type_Def", None), # within Type Construct
    "Final_Binding": ("Derived_Type_Def", None), # within Type Construct
    "Enumerator_Def_Stmt": ("Enum_Def", None), # within Enum_Def
    "Type_Declaration_Stmt": (None, None),
    "Namelist_Stmt": (None, None),
    "Equivalence_Stmt": (None, None),
    "External_Stmt": (None, None),
    "Common_Stmt": (None, None),
    "Bind_Stmt": (None, None),
    "Associate_Stmt": ("Associate_Construct", None), # within associate construct
    "Select_Type_Stmt": ("Select_Type_Construct", None), # within select construct
    "Do_Stmt": (None, ("Cycle_Stmt", "Exit_Stmt")),
    "Label_Do_Stmt": (None, ("Cycle_Stmt", "Exit_Stmt")), # for Cycle_Stmt and Exit_Stmt
    "Format_Stmt": (None, ("Write_Stmt", "Read_Stmt")),
    "Module_Stmt": (None, ("Use_Stmt",)),
    "Use_Stmt": (None, None),
    "Interface_Stmt": (None, None),
    "Import_Stmt": ("Interface_Block", None), # within interface construct
    "Procedure_Declaration_Stmt": (None, None),
    "Function_Stmt": (None, None),
    "Subroutine_Stmt": (None, ("Call_Stmt",)),
    "Entry_Stmt": (None, None),
    "Stmt_Function_Stmt": (None, None)
}

class Referer(pyloco.Task):

    _name_ = "referer"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.resmap = {}
        resmap = os.path.join(os.path.dirname(__file__), "resmap.csv")

        self.add_data_argument("tree", help="tree to search")
        self.add_data_argument("node", help="top node identifier to search")

        self.add_option_argument("--mapfile", default=resmap, help="resoultion map file")

        self.register_forward("ids", help="identifiers collected")

    def perform(self, targs):

        if os.path.isfile(targs.mapfile):
            with open(targs.mapfile) as fh:
                for line in fh:
                    items = line.strip().split(",")

                    if items:
                        _n, _r = items[0], items[1:]
                        res = set()

                        if _r:
                            for _rn in _r:
                                if not _rn:
                                    continue
                                elif _rn == "PASS":
                                    res = PassSet(name_resolvers[_n])
                                else:
                                    res.add(_rn)

                            self.resmap[_n] = res

                        else:
                            self.resmap[_n] = res
        else:
            raise Exception("Resolution map file is not found: %s." % targs.mapfile)

        self.resmap["tuple"] = PassSet()

        self.tree = targs.tree

        ids = {}

        if targs.node:
            self._search(self.tree[targs.node.identifier], ids, set(res_all_stmts.keys()), None)

        self.add_forward(ids=ids)

    def _search(self, node, ids, rtypes, followups=None):

        if node.tag.startswith("End_"):
            return

        if node.tag == "Name":
            ids[node] = (rtypes, followups)
            return

        if node.tag in ("str", "NoneType"):
            return

        rtypes = rtypes & self.resmap[node.tag]

        if node.tag.endswith("_List"):
            for child in self.tree.children(node.identifier):
                self._search(child, ids, set(rtypes))
        else:
            getattr(self, "search_"+node.tag)(node, ids, rtypes)

    def _search_subnodes(self, node, ids, rtypes, includes=[], excludes=[]):

        subnodes = []
        rtypes = rtypes & self.resmap[node.tag]
        children = self.tree.children(node.identifier)

        if includes:
            for item in includes:
                if item in children:
                    subnodes.append(item)

                elif isinstance(item, int) and item < len(children):
                    subnodes.append(children[item])
        else:
            subnodes = children

        for idx, subnode in enumerate(subnodes):

            if idx in excludes or subnode in excludes:
                continue

            self._search(subnode, ids, rtypes)

#    def _search_noname(self, node, ids, rtypes):
#
#        if node.tag != "Name":
#            self._search(node, ids, rtypes)

    def search_Access_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, includes=[1])

    def search_Actual_Arg(self, node, ids, rtypes):
        """
        <actual-arg> = <expr>
                     | <variable>
                     | <procedure-name>
                     | <proc-component-ref>
                     | <alt-return-spec>
        """
        import pdb; pdb.set_trace()
        self._search_subnodes(node, ids, rtypes)

    def search_Actual_Arg_Spec(self, node, ids, rtypes):
        """
        <actual-arg-spec> = [ <keyword> = ] <actual-arg>
        """

        self._search_subnodes(node, ids, rtypes, includes=[1])

    def search_Add_Operand(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, excludes=[1])

    def search_Allocate_Shape_Spec(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Allocate_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Allocation(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_And_Operand(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, includes=[1])

    def search_Array_Constructor(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, includes=[1])

    def search_Array_Section(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Assignment_Stmt(self, node, ids, rtypes):
        """
        <assignment-stmt> = <variable> = <expr>
        """

        self._search_subnodes(node, ids, rtypes, excludes=[1])

    def search_Assumed_Shape_Spec(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Attr_Spec(self, node, ids, rtypes):

        # NOTE: literal string attribute spec
        pass

    def search_Block_Nonlabel_Do_Construct(self, node, ids, rtypes):
        """
         R826_2

        <block-nonlabel-do-construct> = <nonlabel-do-stmt>
                                         [ <execution-part-construct> ]...
                                         <end-do-stmt>
        """
        self._search_subnodes(node, ids, rtypes)


    def search_Call_Stmt(self, node, ids, rtypes):
        """
        <call-stmt> = CALL <procedure-designator>
                      [ ( [ <actual-arg-spec-list> ] ) ]
        """

        self._search_subnodes(node, ids, rtypes)

    def search_Char_Literal_Constant(self, node, ids, rtypes):
        '''
        char-literal-constant is [ kind-param _ ] ' rep-char '
                              or [ kind-param _ ] " rep-char "
        '''

        self._search_subnodes(node, ids, rtypes, includes=[1])

    def search_Comment(self, node, ids, rtypes):
        pass

    def search_Component_Attr_Spec(self, node, ids, rtypes):

        # NOTE: literal string component attribute spec
        pass

    def search_Component_Decl(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, excludes=[0])

    def search_Component_Part(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)
    
    def search_Contains_Stmt(self, node, ids, rtypes):
        pass

    def search_Data_Component_Def_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Data_Ref(self, node, ids, rtypes):

        _followups = []
        _search_subnodes = []
        subnodes = self.tree.children(node.identifier)

        # Part_Ref subnodes
        for pref in subnodes[1:]:
            pref_node = self.tree[pref.identifier]
            if pref_node.tag == "Name":
                _followups.append((pref_node, self.resmap["Part_Ref"]))

            else:
                import pdb; pdb.set_trace()
                pref_subnodes = self.tree.children(pref.identifier)
                pname, sec = pref.subnodes
                _search_subnodes.append(sec)

        self._search(subnodes[0], ids, rtypes, followups=_followups)

        for _s in _search_subnodes:
            self._search(_s, ids, rtypes)

    def search_Deallocate_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Declaration_Type_Spec(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Deferred_Shape_Spec(self, node, ids, rtypes):
        pass

    def search_Derived_Type_Def(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Derived_Type_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, excludes=[1])

    def search_Dimension_Attr_Spec(self, node, ids, rtypes):
        """
        <dimension-attr-spec> = DIMENSION ( <array-spec> )
        """

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[1], ids, rtypes)

    def search_Else_Stmt(self, node, ids, rtypes):
        pass

    def search_Entity_Decl(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, excludes=[0])

    def search_Execution_Part(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Explicit_Shape_Spec(self, node, ids, rtypes):
        """
        <explicit-shape-spec> = [ <lower-bound> : ] <upper-bound>
        """

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[0], ids, rtypes)
        self._search(subnodes[1], ids, rtypes)

    def search_Format(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Function_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, excludes=[1])

    def search_Function_Subprogram(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_If_Construct(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_If_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_If_Then_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Implicit_Part(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Implicit_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Initialization(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[1], ids, rtypes)

    def search_Int_Literal_Constant(self, node, ids, rtypes):
        """
        <int-literal-constant> = <digit-string> [ _ <kind-param> ]
        """

        digit, kind = self.tree.children(node.identifier)
 
        self._search(kind, ids, rtypes)

    def search_Internal_Subprogram_Part(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[1], ids, rtypes)

    def search_Intrinsic_Type_Spec(self, node, ids, rtypes):
        """
        <intrinsic-type-spec> = INTEGER [ <kind-selector> ]
                                | REAL [ <kind-selector> ]
                                | DOUBLE COMPLEX
                                | COMPLEX [ <kind-selector> ]
                                | CHARACTER [ <char-selector> ]
                                | LOGICAL [ <kind-selector> ]
        Extensions:
                                | DOUBLE PRECISION
                                | BYTE
        """

        i_type, selector = self.tree.children(node.identifier)

        # TODO: if selector is to be collected, handle it here
        self._search(selector, ids, rtypes)

    def search_Kind_Selector(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Length_Selector(self, node, ids, rtypes):
        """
        <length -selector> = ( [ LEN = ] <type-param-value> )
                            | * <char-length> [ , ]
        """

        self._search_subnodes(node, ids, rtypes)

    def search_Level_2_Expr(self, node, ids, rtypes):
        """
        <level-2-expr> = [ [ <level-2-expr> ] <add-op> ] <add-operand>
        <level-2-expr> = [ <level-2-expr> <add-op> ] <add-operand>
                         | <level-2-unary-expr>
        <add-op>   = +
                     | -
        """
 
        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[0], ids, rtypes)
        self._search(subnodes[2], ids, rtypes)

    def search_Level_4_Expr(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[0], ids, rtypes)
        self._search(subnodes[2], ids, rtypes)

    def search_Logical_Literal_Constant(self, node, ids, rtypes):
        pass

    def search_Loop_Control(self, node, ids, rtypes):
        """
            R830

            <loop-control> = [ , ] <do-variable> = scalar-int-expr,
                                                   scalar-int-expr
                                                   [ , <scalar-int-expr> ]
                             | [ , ] WHILE ( <scalar-logical-expr> )
        """

        scalar_logical_expr, counter_expr, optional_delim = self.tree.children(node.identifier)

        import pdb; pdb.set_trace()
        if scalar_logical_expr is not None:
            self._search(scalar_logical_expr, ids, rtypes)
        elif counter_expr[0] is not None and counter_expr[1] is not None:
            self._search(counter_expr[0], ids, rtypes)
            self._search(counter_expr[1], ids, rtypes)

    def search_Main_Program(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Module(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Module_Stmt(self, node, ids, rtypes):
        pass

    def search_Module_Subprogram_Part(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Mult_Operand(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        import pdb ;pdb.set_trace()
        self._search(subnodes[0], ids, rtypes)
        self._search(subnodes[2], ids, rtypes)

    def search_Namelist_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Nonlabel_Do_Stmt(self, node, ids, rtypes):
        """
            R829

            <nonlabel-do-stmt> = [ <do-construct-name> : ] DO [ <loop-control> ]
        """

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[1], ids, rtypes)


    def search_NoneType(self, node, ids, rtypes):
        pass

    def search_Part_Ref(self, node, ids, rtypes):
        """
        <part-ref> = <part-name> [ ( <section-subscript-list> ) ]
        """

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[0], ids, rtypes) # assumes rtypes are already specified
        self._search(subnodes[1], ids, rtypes)

    def search_Pointer_Assignment_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Prefix_Spec(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Print_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Procedure_Designator(self, node, ids, rtypes):
        """
        <procedure-designator> = <procedure-name>
                                 | <proc-component-ref>
                                 | <data-ref> % <binding-name>
        """

        subnodes = self.tree.children(node.identifier)

        import pdb; pdb.set_trace()
        if "%" in subnodes:
            idx = subnodes.index("%")
            self._search_subnodes(node, ids, rtypes, includes=subnodes[:idx])
        else:
            self._search_subnodes(node, ids, rtypes)

    def search_Program(self, node, ids, rtypes):
        self._search_subnodes(node, ids, rtypes)

    def search_Program_Stmt(self, node, ids, rtypes):
        pass

    def search_Real_Literal_Constant(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[1], ids, rtypes)

    def search_Save_Stmt(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[1], ids, rtypes)

    def search_Specific_Binding(self, node, ids, rtypes):
        """
        <specific-binding> = PROCEDURE [ ( <interface-name> ) ] [
            [ , <binding-attr-list> ] :: ] <binding-name> [ => <procedure-name> ]

        iname, mylist, dcolon, Binding_Name(line), pname
        """

        subnodes = self.tree.children(node.identifier)

        import pdb; pdb.set_trace()
        if subnodes[4] is None:
            self._search_subnodes(node, ids, rtypes, excludes=[2])
        else:
            self._search_subnodes(node, ids, rtypes, excludes=[2,3])

    def search_Specification_Part(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Structure_Constructor(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        import pdb; pdb.set_trace()

    def search_Structure_Constructor_2(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[1], ids, rtypes)

    def search_Subroutine_Stmt(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes, excludes=[1])

    def search_Subroutine_Subprogram(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Subscript_Triplet(self, node, ids, rtypes):
        """
        <subscript-triplet> = [ <subscript> ] : [ <subscript> ] [ : <stride> ]
        """

        self._search_subnodes(node, ids, rtypes)

    def search_Substring_Range(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Suffix(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[0], ids, rtypes)

    def search_tuple(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Type_Bound_Procedure_Part(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Type_Declaration_Stmt(self, node, ids, rtypes):
        """
        <type-declaration-stmt> = <declaration-type-spec> [
            [ , <attr-spec> ]... :: ] <entity-decl-list>
        """

        subnodes = self.tree.children(node.identifier)

        self._search(subnodes[0], ids, rtypes)
        self._search(subnodes[1], ids, rtypes)

        if subnodes[2].tag != "Name":
            self._search(subnodes[2], ids, rtypes)

    def search_Type_Name(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Type_Param_Value(self, node, ids, rtypes):

        self._search_subnodes(node, ids, rtypes)

    def search_Tuple(self, node, ids, rtypes):

        subnodes = self.tree.children(node.identifier)

        for subnode in subnodes:
            self._search(subnode, ids, rtypes)

    def search_Use_Stmt(self, node, ids, rtypes):
        pass
