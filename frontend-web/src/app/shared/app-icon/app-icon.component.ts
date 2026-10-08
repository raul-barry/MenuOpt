import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  LucideUsers,
  LucideStore,
  LucideLayers,
  LucideFolder,
  LucideCarrot,
  LucideSalad,
  LucideBot,
  LucideHouse,
  LucideClipboardList,
  LucideCalendarDays,
  LucideReceipt,
  LucideReceiptText,
  LucideSlidersHorizontal,
  LucideUserRound,
  LucideCalendarPlus,
  LucideSparkles,
  LucidePackage,
  LucideUtensils,
  LucidePlus,
  LucideMapPin,
  LucidePhone,
  LucideMail,
  LucideShoppingCart,
  LucideChefHat,
  LucideMap,
  LucideLink,
  LucideRefreshCw,
  LucidePencil,
  LucideTrash2,
  LucideLockKeyhole,
  LucideRuler,
  LucideSave,
  LucideCircleCheck,
  LucideX,
  LucideTriangleAlert,
  LucideSearch,
  LucideDollarSign,
  LucideLightbulb,
  LucideSend,
  LucideZap,
  LucideMoveHorizontal,
  LucideClock3,
  LucideCalendarCheck,
  LucideArmchair,
  LucideUtensilsCrossed,
  LucideChartNoAxesCombined,
  LucideInfo,
  LucideCircleHelp,
  LucideStar,
  LucideLoaderCircle,
  LucideIcon,
} from '@lucide/angular';

const ICONS = {
  // Íconos requeridos formalmente por MenuOpt
  house: LucideHouse,
  home: LucideHouse,
  bot: LucideBot,
  utensils: LucideUtensils,
  'clipboard-list': LucideClipboardList,
  list: LucideClipboardList,
  'sliders-horizontal': LucideSlidersHorizontal,
  settings: LucideSlidersHorizontal,
  'calendar-days': LucideCalendarDays,
  calendar: LucideCalendarDays,
  receipt: LucideReceipt,
  'receipt-text': LucideReceiptText,
  'user-round': LucideUserRound,
  user: LucideUserRound,
  'calendar-plus': LucideCalendarPlus,
  sparkles: LucideSparkles,
  store: LucideStore,
  users: LucideUsers,
  carrot: LucideCarrot,
  salad: LucideSalad,
  layers: LucideLayers,
  folder: LucideFolder,

  // Acciones y utilidades generales del sistema
  plus: LucidePlus,
  pin: LucideMapPin,
  phone: LucidePhone,
  mail: LucideMail,
  cart: LucideShoppingCart,
  chef: LucideChefHat,
  map: LucideMap,
  link: LucideLink,
  refresh: LucideRefreshCw,
  edit: LucidePencil,
  trash: LucideTrash2,
  lock: LucideLockKeyhole,
  ruler: LucideRuler,
  save: LucideSave,
  check: LucideCircleCheck,
  close: LucideX,
  alert: LucideTriangleAlert,
  search: LucideSearch,
  money: LucideDollarSign,
  idea: LucideLightbulb,
  send: LucideSend,
  zap: LucideZap,
  move: LucideMoveHorizontal,
  clock: LucideClock3,
  reserve: LucideCalendarCheck,
  table: LucideArmchair,
  menu: LucideUtensilsCrossed,
  package: LucidePackage,
  chart: LucideChartNoAxesCombined,
  info: LucideInfo,
  help: LucideCircleHelp,
  star: LucideStar,
  loader: LucideLoaderCircle,
} as const;

export type AppIconName = keyof typeof ICONS;

@Component({
  selector: 'app-icon',
  standalone: true,
  imports: [CommonModule],
  template: `
    <svg
      xmlns="http://www.w3.org/2000/svg"
      [attr.width]="size"
      [attr.height]="size"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      [attr.stroke-width]="strokeWidth"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="lucide"
      aria-hidden="true"
    >
      @for (child of iconNodes; track $index) {
        @switch (child[0]) {
          @case ('path') {
            <svg:path [attr.d]="child[1]['d']" [attr.opacity]="child[1]['opacity']" />
          }
          @case ('circle') {
            <svg:circle
              [attr.cx]="child[1]['cx']"
              [attr.cy]="child[1]['cy']"
              [attr.r]="child[1]['r']"
              [attr.opacity]="child[1]['opacity']"
            />
          }
          @case ('line') {
            <svg:line
              [attr.x1]="child[1]['x1']"
              [attr.y1]="child[1]['y1']"
              [attr.x2]="child[1]['x2']"
              [attr.y2]="child[1]['y2']"
              [attr.opacity]="child[1]['opacity']"
            />
          }
          @case ('rect') {
            <svg:rect
              [attr.x]="child[1]['x']"
              [attr.y]="child[1]['y']"
              [attr.width]="child[1]['width']"
              [attr.height]="child[1]['height']"
              [attr.rx]="child[1]['rx']"
              [attr.ry]="child[1]['ry']"
              [attr.opacity]="child[1]['opacity']"
            />
          }
          @case ('polyline') {
            <svg:polyline [attr.points]="child[1]['points']" [attr.opacity]="child[1]['opacity']" />
          }
          @case ('polygon') {
            <svg:polygon [attr.points]="child[1]['points']" [attr.opacity]="child[1]['opacity']" />
          }
          @case ('ellipse') {
            <svg:ellipse
              [attr.cx]="child[1]['cx']"
              [attr.cy]="child[1]['cy']"
              [attr.rx]="child[1]['rx']"
              [attr.ry]="child[1]['ry']"
              [attr.opacity]="child[1]['opacity']"
            />
          }
        }
      }
    </svg>
  `,
  host: { class: 'app-icon' },
})
export class AppIconComponent {
  @Input({ required: true }) name!: AppIconName;
  @Input() size = 20;
  @Input() strokeWidth = 2;

  get iconNodes(): any[] {
    const iconEntry = (ICONS as any)[this.name] ?? LucideCircleHelp;
    const data = (iconEntry as any)?.icon ?? (iconEntry as any);
    return data?.node ?? [];
  }
}
