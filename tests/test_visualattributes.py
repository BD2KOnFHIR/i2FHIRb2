# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest


class VisualAttributesTestCase(unittest.TestCase):

    def test_visual_attributes(self):
        from i2fhirb2.i2b2model.visual_attributes import VisualAttributes
        # text, leaf, approximate, draggable, concept
        c1_states = [("LAE", True, False, False, True),
                     ("CAE", False, False, False, True),
                     ("FAE", False, False, True, True),
                     ("MAE", True, True, False, True),
                     ("OAE", False, False, False, False),
                     ("DAE", False, False, True, False),
                     ("RAE", True, False, False, False)]
        for text, leaf, approximate, draggable, concept in c1_states:
            va = VisualAttributes(text)
            self.assertEqual(va.leaf, leaf)
            self.assertEqual(va.approximate, approximate)
            self.assertEqual(va.draggable, draggable)
            self.assertEqual(va.concept, concept)
            va = VisualAttributes()
            va.leaf = leaf
            va.approximate = approximate
            va.draggable = draggable
            va.concept = concept
            self.assertEqual(text, str(va))

        va = VisualAttributes("LAE")
        self.assertTrue(va.active)
        self.assertFalse(va.hidden)
        va = VisualAttributes("LIE")
        self.assertFalse(va.active)
        self.assertFalse(va.hidden)
        va = VisualAttributes("LHE")
        self.assertFalse(va.active)
        self.assertTrue(va.hidden)

        va = VisualAttributes()
        self.assertTrue(va.active)
        self.assertFalse(va.hidden)
        self.assertEqual("FAE", str(va))
        va.active = False
        self.assertEqual("FIE", str(va))
        va.hidden = True
        self.assertEqual("FHE", str(va))

        va = VisualAttributes("LAE")
        self.assertTrue(va.editable)
        va = VisualAttributes("LA ")
        self.assertFalse(va.editable)
        va = VisualAttributes("LA")
        self.assertFalse(va.editable)

        with self.assertRaises(AssertionError):
            _ = VisualAttributes("AAE")
        with self.assertRaises(AssertionError):
            _ = VisualAttributes("LDE")
        with self.assertRaises(AssertionError):
            _ = VisualAttributes("LAH")


if __name__ == '__main__':
    unittest.main()
