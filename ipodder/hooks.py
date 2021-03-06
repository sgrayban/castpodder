# 
# CastPodder hooks
# Copyright (c) 2005-2006 Scott Grayban and the CastPodder Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: hooks.py 127 2006-10-31 07:40:15Z sgrayban $

import logging

log = logging.getLogger('CastPodder.Hooks')

class HookSequence(list): 
    """A sequence of hooks. 

    Calling the `HookSequence` calls all hooks in order."""
    
    def __init__(self, hookCollection, hookCategory): 
        "Initialise the `HookSequence`."
        list.__init__(self)
        self.hookCollection = hookCollection
        self.hookCategory = hookCategory
        
    def __call__(self, *args, **kwargs): 
        "Call all hooks in the `HookSequence`, passing the arguments."

        # Merge our standing arguments with this call's arguments
        allargs = []
        allargs.extend(self.hookCollection.argsForAllHooks)
        allargs.extend(args)
        allkwargs = {}
        allkwargs.update(self.hookCollection.kwargsForAllHooks)
        allkwargs.update(kwargs)
        
        #log.debug("Calling each %s hook as hook(*%s, **%s)", 
        #          repr(self.hookCategory), repr(allargs), 
        #          repr(allkwargs))

        for hook, arguments, keywordArguments in self: 
            #log.debug(" => hook %s", repr(hook))
            allargs.extend(arguments)
            allkwargs.update(keywordArguments)
            hook(*allargs, **allkwargs)
            
class HookCollection(object): 
    """A collection of hook sequences, indexed by hook category."""

    def __init__(self, *argsForAllHooks, **kwargsForAllHooks): 
        "Initialise the `HookCollection` with `hooked` as the hooked object."
        object.__init__(self)
        self.argsForAllHooks = argsForAllHooks
        self.kwargsForAllHooks = kwargsForAllHooks
        self.hooksByCategory = {}
        #log.debug("Initialised hook collection %s", repr(self))

    def reset(self): 
        "Reset the `HookCollection`."
        self.hooksByCategory.clear()
        #log.debug("hook collection %s reset.", repr(self))

    def __getitem__(self, hookCategory): 
        "Fetch a hook sequence by hook category."
        try: 
            res = self.hooksByCategory[hookCategory]
            #log.debug("%s[%s] fetched.", repr(self), repr(hookCategory))
            return res
        except KeyError: 
            #log.debug("hook collection %s lacks category %s; "\
            #          "raising KeyError", repr(self), repr(hookCategory))
            raise

    def get(self, hookCategory):
        """Fetch a hook sequence by hook category, returning an empty sequence 
        if the hook category hasn't been defined yet."""
        try: 
            return self[hookCategory]
        except KeyError: 
            #log.debug("KeyError caught; returning empty HookSequence.")
            return HookSequence(self, hookCategory)
    
    def __call__(self, hookCategory, *arguments, **keywordArguments): 
        "Call all hooks in the sequence for the given category."
        if not self.hooksByCategory.has_key(hookCategory): 
            return
        #log.debug("Calling all hooks in %s.%s", 
        #          repr(self), repr(hookCategory))
        hookSequence = self.get(hookCategory)
        hookSequence(*arguments, **keywordArguments)

    def add(self, hookCategory, hookFunction, *arguments, **keywordArguments): 
        "Append `hookFunction` to the sequence for the given category."
        try: 
            hookSequence = self.hooksByCategory[hookCategory]
        except KeyError: 
            hookSequence = HookSequence(self, hookCategory)
            self.hooksByCategory[hookCategory] = hookSequence
        hookSequence.append((hookFunction, arguments, keywordArguments))

def main(): 
    "Test code."
    logging.basicConfig()
    log.setLevel(logging.DEBUG)
    log.info("Testing...")
    
    hc = HookCollection()
    
    def yell(*a, **kw): 
        log.info("Yell! a=%s; kw=%s", repr(a), repr(kw))
    
    hc.add('yell', yell)
    hc('yell', 1)
    hc('yell', 2)
    hc('noyell', 5)
 
    
if __name__ == '__main__': 
    main()
