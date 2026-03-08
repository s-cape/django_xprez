import { Xprez } from './xprez/core.js';
import { XprezModule } from './xprez/modules.js';
import { XprezSection, XprezSectionSymlink } from './xprez/sections.js';
import { XprezFieldController } from './xprez/fields.js';
import {
    XprezAdderBase,
    XprezAdderItemsBase,
    XprezMultiModuleAdderBase,
    XprezContentAdderBase,
    XprezAdderSelectBase,
    XprezSectionAdderContainerEnd,
    XprezContentAdderSectionBase,
    XprezSectionAdderSectionBefore,
    XprezModuleAdderSectionEnd,
    XprezSectionConfigAdder,
    XprezModuleConfigAdder,
    XprezMultiModuleAdder,
    XprezUploadMultiModuleAdder,
    XprezSectionDuplicateAdder,
    XprezModuleDuplicateAdder,
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
import { XprezShortcutFieldController, XprezShortcutParentMixin } from './xprez/shortcuts.js';
import { XprezMultiModuleItem, XprezMultiModule, XprezUploadMultiModule } from './xprez/multi_module.js';
import { XprezTextModule } from './xprez/text_module.js';
import { xprezExecuteScripts, xprezGetCsrfToken } from './xprez/utils.js';
import { XprezCopyMenu, XprezSectionCopyMenu, XprezModuleCopyMenu, XprezClipboardClip } from './xprez/copy.js';
import { XprezFileInputFieldController } from './xprez/file_input.js';
import { XprezClipboardList } from './xprez/clipboard.js';
import { XprezControllerBase } from './xprez/controller_base.js';

// Root controllers resolvable by name from data-controller attributes
window.Xprez = Xprez;
window.XprezSection = XprezSection;
window.XprezSectionSymlink = XprezSectionSymlink;
window.XprezSectionPopover = XprezSectionPopover;
window.XprezSectionAdderContainerEnd = XprezSectionAdderContainerEnd;
window.XprezSectionAdderSectionBefore = XprezSectionAdderSectionBefore;
window.XprezSectionConfigAdder = XprezSectionConfigAdder;
window.XprezSectionConfig = XprezSectionConfig;
window.XprezSectionCopyMenu = XprezSectionCopyMenu;
window.XprezSectionDuplicateAdder = XprezSectionDuplicateAdder;
window.XprezModuleDuplicateAdder = XprezModuleDuplicateAdder;
window.XprezModuleAdderSectionEnd = XprezModuleAdderSectionEnd;
window.XprezModule = XprezModule;
window.XprezModulePopover = XprezModulePopover;
window.XprezModuleConfigAdder = XprezModuleConfigAdder;
window.XprezModuleConfig = XprezModuleConfig;
window.XprezModuleCopyMenu = XprezModuleCopyMenu;
window.XprezClipboardClip = XprezClipboardClip;
window.XprezTextModule = XprezTextModule;
window.XprezMultiModule = XprezMultiModule;
window.XprezUploadMultiModule = XprezUploadMultiModule;
window.XprezMultiModuleAdder = XprezMultiModuleAdder;
window.XprezUploadMultiModuleAdder = XprezUploadMultiModuleAdder;
window.XprezMultiModuleItem = XprezMultiModuleItem;
window.XprezFieldController = XprezFieldController;
window.XprezFileInputFieldController = XprezFileInputFieldController;
window.XprezShortcutFieldController = XprezShortcutFieldController;
// Public utilities
window.xprezGetCsrfToken = xprezGetCsrfToken;
window.xprezExecuteScripts = xprezExecuteScripts;
window.XprezMultiModuleAdderBase = XprezMultiModuleAdderBase;

export {
    XprezControllerBase,
    Xprez,
    XprezModule,
    XprezSection,
    XprezSectionSymlink,
    XprezFieldController,
    XprezFileInputFieldController,
    XprezAdderBase,
    XprezAdderItemsBase,
    XprezMultiModuleAdderBase,
    XprezContentAdderBase,
    XprezAdderSelectBase,
    XprezSectionAdderContainerEnd,
    XprezContentAdderSectionBase,
    XprezSectionAdderSectionBefore,
    XprezModuleAdderSectionEnd,
    XprezSectionConfigAdder,
    XprezModuleConfigAdder,
    XprezMultiModuleAdder,
    XprezUploadMultiModuleAdder,
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
    XprezShortcutFieldController,
    XprezShortcutParentMixin,
    XprezMultiModuleItem,
    XprezMultiModule,
    XprezUploadMultiModule,
    XprezTextModule,
    XprezClipboardClip,
    XprezClipboardList,
    XprezCopyMenu,
    XprezSectionCopyMenu,
    XprezModuleCopyMenu,
    xprezExecuteScripts,
    xprezGetCsrfToken
};
