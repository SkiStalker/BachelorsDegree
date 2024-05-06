import React, {FC} from "react";

export type IncreasePanelFuncType  = <T>({fetchFunction}: {fetchFunction: () => Promise<T>}) => React.ReactElement;