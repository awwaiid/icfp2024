
open Z
open Printf

let rec from_base94 s =
  let base = Z.of_int 94 in
  let char_to_int c =
    let code = Char.code c in
    if code >= 33 && code <= 126 then Z.of_int (code - 33)
    else failwith "Invalid character in base94 string"
  in
  String.fold_left (fun acc c -> Z.add (Z.mul acc base) (char_to_int c)) Z.zero s

let rec to_base94 n =
  let base = Z.of_int 94 in
  if Z.equal n Z.zero then "!"
  else
    let rec aux n acc =
      if Z.equal n Z.zero then acc
      else
        let digit = Z.rem n base in
        let char = Char.chr (Z.to_int digit + 33) in
        aux (Z.div n base) (String.make 1 char ^ acc)
    in
    aux n ""

let raw_encode_string s =
  "S" ^ String.map (fun c -> Char.chr ((Char.code c + 33) mod 94 + 33)) s

let raw_parse_string s =
  String.map (fun c -> Char.chr ((Char.code c - 33 + 94) mod 94)) (String.sub s 1 (String.length s - 1))

let raw_encode_integer n =
  "I" ^ to_base94 n

let remainder a b =
  let sign_a = Z.sign a in
  let sign_b = Z.sign b in
  let abs_rem = Z.rem (Z.abs a) (Z.abs b) in
  if sign_a >= 0 then abs_rem else Z.neg abs_rem

let result = (fun () -> ((fun () -> (fun v1 -> (fun () -> v1 ()) ())) ()) ((fun () -> Z.sub ((fun () -> Z.of_int 7) ()) ((fun () -> Z.of_int 2) ())))) ()

let () =
  match result with
  | `Int n -> printf "%s\n" (Z.to_string n)
  | `Bool b -> printf "%b\n" b
  | `String s -> printf "%s\n" s
