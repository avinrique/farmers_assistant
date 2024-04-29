import { ServerTranslateOptions } from "./types/ServerTranslateOptions";
import { TranslationResult } from "./types/TranslationResult";
export declare function translate(text: string, options?: ServerTranslateOptions): Promise<TranslationResult>;
