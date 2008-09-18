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

logging.basicConfig(level=logging.DEBUG)

def fetch():
    logging.info("Commencing fetch.")
    personas = OnlinePersona.objects.all()
    for persona in personas:
        logging.info("Fetching accounts related to \"%s\"" % persona.name)
        accounts = persona.accounts()
        for account in accounts:
            if not account.active:
                logging.info("Skipping inactive %s account \"%s\"" % (account.service, account))
                continue
            
            logging.info("Fetching activity from %s account \"%s\"" % (account.service, account))
            
            modulename = "djangregator.services.%s_sync" % account.service
            try:
                module = __import__(modulename, globals(), locals(), ['fetch'])
            except:
                logging.exception("Unable to load a backend for syncing with %s. Skipping..." % account.service)
                continue
                
            (created, existing) = module.fetch(account)
            logging.info('%s: synced %s new, %s existing' % (account.service, created, existing))
    logging.info("Fetch complete.")