import { Xprez } from './xprez/core.js';
import { XprezContent } from './xprez/content.js';
import { XprezSection } from './xprez/sections.js';
import {
    XprezAddBase,
    XprezAddContainerEnd,
    XprezAddSectionBase,
    XprezAddSectionBefore,
    XprezAddSectionEnd
} from './xprez/adders.js';
import {
    XprezDeleterBase,
    XprezSectionDeleter,
    XprezContentDeleter
} from './xprez/deleters.js';
import {
    XprezPopoverBase,
    XprezSectionPopover,
    XprezContentPopover
} from './xprez/popovers.js';
import {
    XprezConfigBase,
    XprezSectionConfig,
    XprezContentConfig
} from './xprez/configs.js';
import { XprezSortable } from './xprez/sortable.js';
import { executeScripts } from './xprez/utils.js';

window.Xprez = Xprez;
window.XprezContent = XprezContent;

export {
    Xprez,
    XprezContent,
    XprezSection,
    XprezAddBase,
    XprezAddContainerEnd,
    XprezAddSectionBase,
    XprezAddSectionBefore,
    XprezAddSectionEnd,
    XprezDeleterBase,
    XprezSectionDeleter,
    XprezContentDeleter,
    XprezPopoverBase,
    XprezSectionPopover,
    XprezContentPopover,
    XprezConfigBase,
    XprezSectionConfig,
    XprezContentConfig,
    XprezSortable,
    executeScripts
};
