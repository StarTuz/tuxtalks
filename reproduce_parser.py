
import xml.etree.ElementTree as ET

xml_data = """
<Root>
    <CycleFireGroupPrevious>
        <Primary Device="Keyboard" Key="Key_LeftControl">
             <Modifier Device="Keyboard" Key="Key_26" />
        </Primary>
        <Secondary Device="{NoDevice}" Key="" />
    </CycleFireGroupPrevious>
    <IncreaseEnginesPower>
        <Primary Device="SaitekX52" Key="Joy_27" />
        <Secondary Device="{NoDevice}" Key="" />
    </IncreaseEnginesPower>
    <IncreaseWeaponsPower>
        <Primary Device="Keyboard" Key="Key_26" />
    </IncreaseWeaponsPower>
</Root>
"""

class MockProfile:
    def load_bindings(self):
        root = ET.fromstring(xml_data)
        self.actions = {}
        
        for child in root:
            tag = child.tag
            internal_id = tag
            
            primary = child.find('Primary')
            secondary = child.find('Secondary')
            
            candidates = []
            if primary is not None and primary.get('Device') == "Keyboard": candidates.append(primary)
            if secondary is not None and secondary.get('Device') == "Keyboard": candidates.append(secondary)
            
            if candidates:
                bind = candidates[0]
                key = bind.get('Key')
                print(f"Found Keyboard bind for {internal_id}: {key}")
            else:
                print(f"No Keyboard bind for {internal_id}")
                # Check for Controller?
                if primary is not None and primary.get('Device') != "{NoDevice}":
                     print(f"  -> Found Controller on Primary: {primary.get('Device')} Key={primary.get('Key')}")

mock = MockProfile()
mock.load_bindings()
