import { Xprez } from './xprez/core.js';
import { XprezModule } from './xprez/modules.js';
import { XprezSection } from './xprez/sections.js';
import { XprezFieldController } from './xprez/fields.js';
import {
    XprezAdderBase,
    XprezAdderItemsBase,
    XprezAdderSelectBase,
    XprezAdderContainerEnd,
    XprezAdderSectionBase,
    XprezAdderSectionBefore,
    XprezAdderSectionEnd,
    XprezSectionConfigAdder
} from './xprez/adders.js';
import {
    XprezDeleterBase,
    XprezSectionDeleter,
    XprezModuleDeleter
} from './xprez/deleters.js';
import {
    XprezPopoverBase,
    XprezSectionPopover,
    XprezModulePopover
} from './xprez/popovers.js';
import {
    XprezConfigBase,
    XprezSectionConfig,
    XprezModuleConfig,
    XprezConfigParentMixin
} from './xprez/configs.js';
import { XprezSortable } from './xprez/sortable.js';
import { XprezSyncManager, XprezModuleSyncMixin } from './xprez/sync.js';
import { XprezMultiModuleItem, XprezMultiModule, XprezUploadMultiModule } from './xprez/multi_module.js';
import { XprezTextModule } from './xprez/text_module.js';
import { executeScripts } from './xprez/utils.js';
import { XprezFileInputFieldController } from './xprez/file_input.js';

window.Xprez = Xprez;
window.XprezModule = XprezModule;
window.XprezTextModule = XprezTextModule;
window.XprezFieldController = XprezFieldController;
window.XprezFileInputFieldController = XprezFileInputFieldController;
window.XprezMultiModuleItem = XprezMultiModuleItem;
window.XprezMultiModule = XprezMultiModule;
window.XprezUploadMultiModule = XprezUploadMultiModule;

export {
    Xprez,
    XprezModule,
    XprezSection,
    XprezFieldController,
    XprezFileInputFieldController,
    XprezAdderBase,
    XprezAdderItemsBase,
    XprezAdderSelectBase,
    XprezAdderContainerEnd,
    XprezAdderSectionBase,
    XprezAdderSectionBefore,
    XprezAdderSectionEnd,
    XprezSectionConfigAdder,
    XprezDeleterBase,
    XprezSectionDeleter,
    XprezModuleDeleter,
    XprezPopoverBase,
    XprezSectionPopover,
    XprezModulePopover,
    XprezConfigBase,
    XprezSectionConfig,
    XprezModuleConfig,
    XprezConfigParentMixin,
    XprezSortable,
    XprezSyncManager,
    XprezModuleSyncMixin,
    XprezMultiModuleItem,
    XprezMultiModule,
    XprezUploadMultiModule,
    XprezTextModule,
    executeScripts
};
