import { Xprez } from './xprez/core.js';
import { XprezModule } from './xprez/module.js';
import { XprezSection } from './xprez/sections.js';
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
    XprezModuleConfig
} from './xprez/configs.js';
import { XprezSortable } from './xprez/sortable.js';
import { executeScripts } from './xprez/utils.js';

window.Xprez = Xprez;
window.XprezModule = XprezModule;

export {
    Xprez,
    XprezModule,
    XprezSection,
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
    XprezSortable,
    executeScripts
};
