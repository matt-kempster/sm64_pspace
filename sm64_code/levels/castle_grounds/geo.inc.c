#include "levels/wdw/header.h"

#include "levels/castle_grounds/area_1/geo.inc.c"

#include "levels/castle_grounds/area_2/geo.inc.c"


// TODO - shouldn't this technically be in its own file?
const GeoLayout water_level_dimond_geo[] = {
    GEO_CULLING_RADIUS(200),
    GEO_OPEN_NODE(),
        GEO_SHADOW(SHADOW_SQUARE_SCALABLE, 0x96, 90),
        GEO_OPEN_NODE(),
            GEO_DISPLAY_LIST(LAYER_TRANSPARENT, wdw_seg7_dl_070131B8),
        GEO_CLOSE_NODE(),
    GEO_CLOSE_NODE(),
    GEO_END(),
};