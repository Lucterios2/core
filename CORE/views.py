# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from django.utils.translation import ugettext as tt

from lucterios.framework.tools import describ_action, add_sub_menu, FORMTYPE_NOMODAL
from lucterios.framework.xferbasic import XferContainerMenu, XferContainerAcknowledge

add_sub_menu('core.general', '', 'general.png', tt('General'), tt('Generalite'))
add_sub_menu('core.admin', '', 'admin.png', tt('Administration'), tt('Adminitration des configurations et des reglages.'))

@describ_action('')
class Menu(XferContainerMenu):
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():        
            return XferContainerMenu.get(self, request, *args, **kwargs)
        else:
            from lucterios.CORE.views_auth import Authentification
            auth = Authentification()
            return auth.get(request, *args, **kwargs)

@describ_action('', FORMTYPE_NOMODAL, 'core.general' , tt("Changement de votre mot de passe."))
class Changerpassword(XferContainerAcknowledge):
    caption = tt("_Mot de passe")
    icon = "passwd.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.admin' , tt("Visualisation et modification des parametres generaux."))
class Configuration(XferContainerAcknowledge):
    caption = tt("Configuration _generale")
    icon = "config.png"

add_sub_menu("core.archivage", 'core.admin', "backup.png", tt("Archivage"), tt("Outils de sauvegarde et de restoration des donnees."))

@describ_action('', FORMTYPE_NOMODAL, 'core.archivage' , tt("Sauvegarde manuelle des donnees du logiciel."))
class SelectNewArchive(XferContainerAcknowledge):
    caption = tt("_Sauvegarder")
    icon = "backup_save.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.archivage' , tt("Restauration d'une archive."))
class SelectRestor(XferContainerAcknowledge):
    caption = tt("_Restauration")
    icon = "backup_restor.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.archivage' , tt("Importer ou telecharger des archives de sauvegarde."))
class ToolBackup(XferContainerAcknowledge):
    caption = tt("_Gestion des archives")
    icon = "backup_tool.png"

add_sub_menu("core.extensions", 'core.admin', "config_ext.png", tt("_Extensions (conf.)"), tt("Gestion des configurations des differentes modules."))

add_sub_menu("core.print", 'core.admin', "PrintReport.png", tt("_Rapport et Impression"), tt("Gestion de vos rapports et des outils d'impression."))

@describ_action('', FORMTYPE_NOMODAL, 'core.print' , tt("Gestion des differents modeles d'impression."))
class PrintmodelList(XferContainerAcknowledge):
    caption = tt("_Modeles des rapports")
    icon = "PrintReportModel.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.print' , tt("Reedition des anciennes impressions sauvegardees"))
class FinalreportList(XferContainerAcknowledge):
    caption = tt("_Ra_pports sauvegardes")
    icon = "PrintReportSave.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.print' , tt("Gestion des planches d'etiquettes"))
class EtiquettesListe(XferContainerAcknowledge):
    caption = tt("_Etiquettes")
    icon = "PrintReportLabel.png"

add_sub_menu("core.right" , 'core.admin', "gestionDroits.png", tt("_Gestion des Droits"), 
             tt("Gestion des utilisateurs et de leurs droits selon les modules."))

@describ_action('', FORMTYPE_NOMODAL, 'core.right' , tt("Gestion d'un groupe de droits d'acces."))
class GroupListe(XferContainerAcknowledge):
    caption = tt("_Groupes")
    icon = "group.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.right' , tt("Gestion des utilisateurs autorises a se connecter."))
class UsersList(XferContainerAcknowledge):
    caption = tt("_Utilisateurs")
    icon = "user.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.right' , tt("Gestion des modules et association des droits."))
class ExtensionList(XferContainerAcknowledge):
    caption = tt("_Extensions")
    icon = "extensions.png"
