# Copyright (c) 2008, Idan Gazit
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of the author nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from djangregator.models import *
import logging
import sys

def fetch():
    logger = logging.getLogger("Fetch")
    success_total = 0
    fail_total = 0
    logger.info("Commencing fetch.")
    personas = OnlinePersona.objects.all()
    for persona in personas:
        success_persona = 0
        fail_persona = 0
        logger.info("Fetching accounts related to \"%s\"" % persona.name)
        accounts = persona.accounts()
        
        if accounts.count == 0:
            logger.info('Persona "%s" has no defined accounts. Skipping...' % persona.name)
            continue
        
        for account in accounts:
            if not account.active:
                logger.info("Skipping inactive %s account \"%s\"" % (account.service, account))
                continue
            
            logger.info("Fetching activity from %s account \"%s\"" % (account.service, account))
            
            modulename = "djangregator.services.%s" % account.service
            try:
                module = __import__(modulename, globals(), locals(), ['fetch'])
            except ImportError:
                fail_persona += 1
                fail_total += 1
                logger.error("Unable to load a backend for fetching from %s. Skipping..." % account.service)
                continue
            
            try:
                (created, existing) = module.fetch(account)
                logger.info('%s: fetched %d new, skipped %d existing' % (account.service, created, existing))
            except:
                fail_persona += 1
                fail_total += 1
                exc_type, exc_value = sys.exc_info()[:2]
                logger.exception('Failed to fetch activity from %s account "%s": %s: "%s"' % 
                (account.service,
                account,
                exc_type.__name__,
                exc_value if exc_value else "no additional information"))
            else:
                success_persona += 1
                success_total += 1
        
        persona_report = '--- Persona "%s" fetch report: %d OK, %d failures.'
        if not fail_persona:
            logger.info(persona_report % (persona.name, success_persona, fail_persona))
        else:
            logger.warn(persona_report % (persona.name, success_persona, fail_persona))
    
    if not fail_total:
        logger.info('=== Fetch completed with no errors: %s personas / %d accounts.' % (personas.count, success_total))
    else:
        logger.warn('=== Fetch completed with some errors: %s personas / %d accounts OK / %d accounts failed' %
        (personas.count(), success_total, fail_total))